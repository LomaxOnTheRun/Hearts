from game import *

def get_Q_key(state_str, action):
	"""Returns string representation of trick and valid choices (i.e. state)"""
	return state_str + '_' + action


def get_Q_value(Q, key, game_data=False):
	"""Return Q value if exists, otherwise create one"""
	if key in Q:
		return Q[key]
	else:
		Q[key] = 0
		return 0


def get_state_str(trick, players, game_data):
	player0 = get_player(players, 0)
	legal_moves = player0.get_legal_moves(trick, game_data)
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


def update_Q(Q, old_state_str, old_action, learning_rate, reward, discount_factor, new_state_str, game_data, legal_moves):
	"""Does what it says on the tin"""
	# Get old_Q_value
	old_Q_key = get_Q_key(old_state_str, old_action)
	old_Q_value = get_Q_value(Q, old_Q_key)
	# Get max Q_value for new state
	if new_state_str is 'terminal':
		max_next_Q_value = 0
	else:
		next_Q_keys = [get_Q_key(new_state_str, move) for move in legal_moves]
		next_Q_values = [get_Q_value(Q, key, game_data) for key in next_Q_keys]
		max_next_Q_value = max(next_Q_values)
	# Get new Q value
	new_Q_value = old_Q_value + learning_rate * (reward + discount_factor * max_next_Q_value - old_Q_value)
	Q[old_Q_key] = new_Q_value
	if game_data['show_Q_values']:
		print('{} -> {}'.format(old_Q_key, new_Q_value))


def show_Q(Q):
	keys = list(Q.keys())
	keys.sort()
	for key in keys:
		print('{} : {}'.format(key, Q[key]))





