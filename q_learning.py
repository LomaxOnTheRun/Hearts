from game import *
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation

from random import random, choice

import os

# Get rid of annoying Keras logging
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# For hands_list = [['SJ', 'SQ'], ['S10', 'SK']]
#
# Q:
#	S10_SJSQ_SJ : 0.0
#	S10_SJSQ_SQ : -11.7
#	S10_SJ_SJ : 0.0
#	S10_SQ_SQ : -13.0
#	SK_SJSQ_SJ : -11.7
#	SK_SJSQ_SQ : 0.0
#	_SJ_SJ : 0.0
#	_SQ_SQ : 0.0

# Future thoughts:
# - Maybe instead of the last two state groups, have:
#  -> 0 for N/A
#  -> -1 for available to play but not played
#  -> +1 for played
#  since 'played' will always be a subgroup of 'available to play'


def get_player0_choice(players, game, trick, model):
	"""Gets greedy choice"""
	player0 = get_player(players, 0)
	#player0_card_code = input('This is your hand:\n{}\nCard to play: '.format(player0.get_hand_codes()))
	#card_code = player0.get_random_legal_card_to_play(trick, game)
	#return card_code
	legal_moves = player0.get_legal_moves(trick, game)
	state_str = get_state_str(trick, players, game)
	Q_keys = [get_Q_key(state_str, move) for move in legal_moves]
	# Q values, from the output of the neural network
	Q_values = [get_NN_output(model, key, game) for key in Q_keys]
	if game.show_Q_values:
		for i in range(len(Q_keys)):
			print('{} -> {}'.format(Q_keys[i], Q_values[i]))
	max_Q_value = max(Q_values)
	# Choose
	best_moves = []
	other_moves = []
	for index, value in enumerate(Q_values):
		move = legal_moves[index]
		if value == max_Q_value:
			best_moves.append(move)
		else:
			other_moves.append(move)
	# Choose move with appropriate greediness
	if random() < game.greediness or not other_moves:
		chosen_move = choice(best_moves)
	else:
		chosen_move = choice(other_moves)
	return chosen_move


def get_Q_key(state_str, action):
	"""Returns string representation of trick and valid choices (i.e. state)"""
	return state_str + '_' + action


def get_state_str(trick, players, game):
	player0 = get_player(players, 0)
	legal_moves = player0.get_legal_moves(trick, game)
	# For the debug version, tricks can just be ordered,
	# since we're only playing with hearts
	# Actually, since the first card already influences our legal
	# moves, we can just order all of the cards in the trick to give
	# us fewer states
	trick_copy = list(trick)
	sort_values = [card.sort_value for card in trick_copy]
	while sort_values:
		min_index = sort_values.index(min(sort_values))
		trick_copy.append(trick_copy.pop(min_index))
		del sort_values[min_index]
	state_str = \
		''.join([card.code for card in trick_copy]) + '_' + \
		''.join(legal_moves) + '_' + \
		''.join([card.code for card in game.cards_in_other_hands])
	return state_str


def get_reward(player0_points):
	"""Get reward from trick"""
	return -player0_points


def update_Q(old_state_str, old_action, reward, new_state_str, game, legal_moves, model):
	"""Does what it says on the tin

	TODO: CHANGE THIS TO UN-SIGMOID VALUE TO GET 'OLD_Q_VALUE' WHICH GETS USED FOR EQUATIONS,
		  THEN RE-SIGMOID IT TO GET VALUE TO TRAIN NETWORK WITH

	"""
	# Get old Q value
	old_Q_key = get_Q_key(old_state_str, old_action)
	old_Q_value = get_NN_output(model, old_Q_key, game)

	# Get max Q_value for new state
	if new_state_str is 'terminal':
		max_next_Q_value = 0
	else:
		next_Q_keys = [get_Q_key(new_state_str, move) for move in legal_moves]
		next_Q_values = [get_NN_output(model, key, game) for key in next_Q_keys]
		max_next_Q_value = max(next_Q_values)

	# Get new Q value
	new_Q_value = old_Q_value + game.learning_rate * (reward + game.discount_factor * max_next_Q_value - old_Q_value)
	model.fit(get_Q_state(old_Q_key, game), new_Q_value, epochs=1, verbose=0)
	if game.show_Q_values:
		print('{} -> {}'.format(old_Q_key, new_Q_value))


def show_Q(model, game):
	# TODO: To use this, need to create these from game.unique_hand_codes +
	#		cards played in trick + card played
	keys = create_keys()  # This doesn't exist yet...
	keys.sort()
	row_format ="{:>15}" * 2
	print()
	for key in keys:
		NN_value = '{} (NN)'.format(round(float(get_NN_output(model, key, game)[0][0]), 2))
		print(row_format.format(key, Q_value, NN_value))
	print()


############################
#                          #
#   NEURAL NETWORK STUFF   #
#                          #
############################


# NN structure for 4 cards:
# - 12 binary inputs (trick, legal moves, card played)
#   - 4 binary inputs for each category (one per card in play)
# - Hidden layer (? nodes, starting with 20)
# - 1 linear output, value of that play
#   - Equivalent of current Q value

# NOTE: For P2 always playing lowest value, P1 should get 36.67% of the points
#       For P2 always playing highest value, P1 should get 48.33% of the points
# These values have been calculated by hand
#
# For 2 players, 4 cards each, lowest card, fewest % of points is 33.21%
#  - 10000 not enough, 100000 enough


def create_network_model(game, optimizer='sgd', loss='mse'):  # Not sure about these
	model = Sequential()
	model.add(Dense(200,
					activation='relu',
					input_shape=(4 * len(game.deck),)))
	model.add(Dense(1, activation='linear'))
	model.compile(optimizer=optimizer,
				  loss=loss,
				  metrics=['accuracy'])
	return model


def get_Q_state(Q_key, game):
	Q_state_array = state_str_to_array(Q_key, game)
	Q_state = np.array(Q_state_array)
	Q_state = Q_state.reshape(1, 4 * len(game.deck))
	return Q_state


def get_NN_output(model, old_Q_key, game):
	input_vector = get_Q_state(old_Q_key, game)
	return model.predict(input_vector, batch_size=1)


def state_str_to_array(state_str, game):
	deck_codes = get_ordered_deck_codes(game)
	num_cards = len(deck_codes)
	binary_array = []
	for section in state_str.split('_'):
		for code in deck_codes:
			if code in section:
				binary_array += [1]
			else:
				binary_array += [0]
	return binary_array


def array_to_state_str(array, game):
	deck_codes = get_ordered_deck_codes(game)
	num_cards = len(deck_codes)
	sections = [array[offset:offset+num_cards] for offset in range(0, len(array), num_cards)]
	state_str = ''
	for section in sections:
		for index, include in enumerate(section):
			if include:
				state_str += deck_codes[index]
		state_str += '_'
	return state_str[:-1]

###########
# TESTING #
###########

def test_model(game, model):
	"""Runs all unique combinations of hands once with greedy network, returns single percentage points value"""
	# Run a single hand for each hand set
	total_points = [0] * game.num_players
	for hand_codes in game.unique_hand_codes:
		points = run_single_greedy_hand(game.num_players, hand_codes, model)
		total_points = [sum(x) for x in zip(total_points, points)]
	percentage_points = get_percentage_points(total_points)
	return percentage_points


def run_single_greedy_hand(num_players, hand_codes, model):
	"""Run a single hand with no learning, returns points"""
	game = Game(num_players=num_players, greediness=1.0, num_hands=1)
	players = set_up_game(game)
	players = game.set_hands(hand_codes)
	while players[0].hand:
		trick = start_trick(players, game)
		action = get_player0_choice(players, game, trick, model)
		player0_points = finish_trick(players, game, trick, action)
	reset_player_order(players)
	points = [player.points for player in players]
	return points
