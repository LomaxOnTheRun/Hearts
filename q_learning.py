from game import *


def get_player0_choice(players, game, trick, Q):
	"""Gets greedy choice"""
	player0 = get_player(players, 0)
	#player0_card_code = input('This is your hand:\n{}\nCard to play: '.format(player0.get_hand_codes()))
	#card_code = player0.get_random_legal_card_to_play(trick, game)
	#return card_code
	legal_moves = player0.get_legal_moves(trick, game)
	state_str = get_state_str(trick, players, game)
	Q_keys = [get_Q_key(state_str, move) for move in legal_moves]
	Q_values = [get_Q_value(Q, key) for key in Q_keys]
	if game.show_Q_values:
		for i in range(len(Q_keys)):
			print('{} -> {}'.format(Q_keys[i], Q_values[i]))
	max_Q_value = max(Q_values)
	best_moves = []
	for index, value in enumerate(Q_values):
		if value == max_Q_value:
			best_moves.append(legal_moves[index])
	chosen_move = choice(best_moves)
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


def update_Q(Q, old_state_str, old_action, reward, new_state_str, game, legal_moves):
	"""Does what it says on the tin"""
	# Get old_Q_value
	old_Q_key = get_Q_key(old_state_str, old_action)
	old_Q_value = get_Q_value(Q, old_Q_key)
	# Get max Q_value for new state
	if new_state_str is 'terminal':
		max_next_Q_value = 0
	else:
		next_Q_keys = [get_Q_key(new_state_str, move) for move in legal_moves]
		next_Q_values = [get_Q_value(Q, key) for key in next_Q_keys]
		max_next_Q_value = max(next_Q_values)
	# Get new Q value
	new_Q_value = old_Q_value + game.learning_rate * (reward + game.discount_factor * max_next_Q_value - old_Q_value)
	Q[old_Q_key] = new_Q_value
	if game.show_Q_values:
		print('{} -> {}'.format(old_Q_key, new_Q_value))


def show_Q(Q):
	keys = list(Q.keys())
	keys.sort()
	for key in keys:
		print('{} : {}'.format(key, Q[key]))





