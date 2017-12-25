from game import *
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation

# For hands_list = [['SJ', 'SQ'], ['S10', 'SK']]
# 
# Q: 
#	S10_SJSQ_SJ : 0.0
#	S10_SJSQ_SQ : -1.3
#	S10_SJ_SJ : 0.0
#	S10_SQ_SQ : -2.4699999999999998
#	SK_SJSQ_SJ : -0.11700000000000002
#	SK_SJSQ_SQ : 0.0
#	_SJ_SJ : 0.0
#	_SQ_SQ : 0.0


# Future thoughts:
# - Maybe instead of the last two, have:
#  -> 0 for N/A
#  -> -1 for available to play but not played
#  -> +1 for played
#  since 'played' will always be a subgroup of 'available to play'


def get_player0_choice(players, game, trick, Q, model):
	"""Gets greedy choice"""
	player0 = get_player(players, 0)
	#player0_card_code = input('This is your hand:\n{}\nCard to play: '.format(player0.get_hand_codes()))
	#card_code = player0.get_random_legal_card_to_play(trick, game)
	#return card_code
	legal_moves = player0.get_legal_moves(trick, game)
	state_str = get_state_str(trick, players, game)
	Q_keys = [get_Q_key(state_str, move) for move in legal_moves]
	# Q values
	Q_values = [get_Q_value(Q, key) for key in Q_keys]
	if game.show_Q_values:
		for i in range(len(Q_keys)):
			print('{} -> {}'.format(Q_keys[i], Q_values[i]))
	max_Q_value = max(Q_values)
	# NN values
	NN_values = [get_NN_output(model, key, game) for key in Q_keys]
	if game.show_NN_values:
		for i in range(len(Q_keys)):
			print('{} -> {}'.format(Q_keys[i], Q_values[i]))
	max_NN_value = max(NN_values)
	# Choose
	best_moves = []
	other_moves = []
#	for index, value in enumerate(Q_values):
	for index, value in enumerate(NN_values):
		move = legal_moves[index]
#		if value == max_Q_value:
		if value == max_NN_value:
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


def get_Q_value(Q, key):
	"""Return Q value if exists, otherwise create one"""
	if key in Q:
		return Q[key]
	else:
		Q[key] = 0
		return 0


def get_state_str(trick, players, game):
	player0 = get_player(players, 0)
	legal_moves = player0.get_legal_moves(trick, game)
	# For the debug version, tricks can just be ordered,
	# since we're only playing with hearts
	# Actually, since the first card already influences our legal
	# moves, we can just order all of the cards in the trick to give
	# us fewer states
	#return ''.join([card.code for card in trick]) + '_' + ''.join(legal_moves)
	trick_copy = list(trick)
	sort_values = [card.sort_value for card in trick_copy]
	while sort_values:
		min_index = sort_values.index(min(sort_values))
		trick_copy.append(trick_copy.pop(min_index))
		del sort_values[min_index]
	return ''.join([card.code for card in trick_copy]) + '_' + ''.join(legal_moves)


def get_reward(player0_points):
	"""Get reward from trick"""
	return -player0_points


def update_Q(Q, old_state_str, old_action, reward, new_state_str, game, legal_moves, model):
	"""Does what it says on the tin
	
	TODO: CHANGE THIS TO UN-SIGMOID VALUE TO GET 'OLD_Q_VALUE' WHICH GETS USED FOR EQUATIONS,
		  THEN RE-SIGMOID IT TO GET VALUE TO TRAIN NETWORK WITH
	
	"""
	# Get old_Q_value
	old_Q_key = get_Q_key(old_state_str, old_action)
	old_Q_value = get_Q_value(Q, old_Q_key)
	old_NN_value = get_NN_output(model, old_Q_key, game)
	
	# Get max Q_value for new state
	if new_state_str is 'terminal':
		max_next_Q_value = 0
		max_next_NN_value = 0
	else:
		next_Q_keys = [get_Q_key(new_state_str, move) for move in legal_moves]
		next_Q_values = [get_Q_value(Q, key) for key in next_Q_keys]
		next_NN_values = [get_NN_output(model, key, game) for key in next_Q_keys]
		max_next_Q_value = max(next_Q_values)
		max_next_NN_value = max(next_NN_values)
	
	# Get new Q value
	new_Q_value = old_Q_value + game.learning_rate * (reward + game.discount_factor * max_next_Q_value - old_Q_value)
	new_NN_value = old_NN_value + game.learning_rate * (reward + game.discount_factor * max_next_NN_value - old_NN_value)
	Q[old_Q_key] = new_Q_value
	model.fit(get_NN_state(old_Q_key, game), new_NN_value, epochs=1, verbose=0)
	if game.show_Q_values:
		print('{} -> {}'.format(old_Q_key, new_Q_value))


def show_Q(Q, model, game):
	keys = list(Q.keys())
	keys.sort()
	row_format ="{:>15}" * 3
	print()
	for key in keys:
		Q_value = '{} (Q)'.format(round(Q[key], 2))
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


def create_network_model(game):
	model = Sequential()
	model.add(Dense(20,
					activation='relu',
					input_shape=(3 * len(game.deck),)))
	model.add(Dense(1, activation='linear'))
	model.compile(optimizer='sgd',		# Not sure about this
				  loss='mse',			# Not sure about this either
				  metrics=['accuracy'])
	return model


def get_NN_state(Q_key, game):
	NN_state = state_str_to_array(Q_key, game)
	NN_state = np.array(NN_state)
	NN_state = NN_state.reshape(1, 3 * len(game.deck))
	return NN_state


def get_NN_output(model, old_Q_key, game):
	input_vector = get_NN_state(old_Q_key, game)
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












