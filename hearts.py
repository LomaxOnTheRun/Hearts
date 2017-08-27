from display_utils import *
from game import *

# NOTES:
# - I'm not shooting the moon for now (more complex), when I do:
#   - Need to think of how to reward / punish (-26*4 points at end?)
#   - Keep track of more history (other player scores / previously tricks)
# - I'm not passing cards across at the start of hands (more complex)


def get_player0_choice(players, game_data, trick, Q):
	"""Gets greedy choice"""
	player0 = get_player(players, 0)
	#player0_card_code = input('This is your hand:\n{}\nCard to play: '.format(player0.get_hand_codes()))
	#card_code = player0.get_random_legal_card_to_play(trick, game_data)
	#return card_code
	legal_moves = player0.get_legal_moves(trick, game_data)
	state = get_state(trick, players, game_data)
	Q_keys = [get_Q_key(state, move) for move in legal_moves]
	Q_values = [get_Q_value(Q, key) for key in Q_keys]
	max_Q_value = max(Q_values)
	best_moves = []
	for index, value in enumerate(Q_values):
		if value == max_Q_value:
			best_moves.append(legal_moves[index])
	chosen_move = choice(best_moves)
	return chosen_move


def get_Q_key(state, action):
	"""Returns string representation of trick and valid choices (i.e. state)"""
	trick = [card.code for card in state['trick']]
	return ''.join(trick) + '_' + \
		   ''.join(state['legal_moves']) + '_' +\
		   action

def get_Q_value(Q, key, game_data=False):
	"""Return Q value if exists, otherwise create one"""
	if key in Q:
		#if game_data:
		#	print('Value seen before: {} ({})'.format(key, game_data['game_num']))
		return Q[key]
	else:
		Q[key] = 0
		return 0

def get_state(trick, players, game_data):
	player0 = get_player(players, 0)
	legal_moves = player0.get_legal_moves(trick, game_data)
	return {'trick': trick, 'legal_moves': legal_moves}

def get_reward(player0_points):
	"""Get reward from trick"""
	return -player0_points

def update_Q(Q, old_state, old_action, learning_rate, reward, discount_factor, new_state, game_data):
	"""Does what it says on the tin"""
	# Get old_Q_value
	old_Q_key = get_Q_key(old_state, old_action)
	old_Q_value = get_Q_value(Q, old_Q_key)
	# Get max Q_value for new state
	legal_moves = new_state['legal_moves']
	next_Q_keys = [get_Q_key(new_state, move) for move in legal_moves]
	next_Q_values = [get_Q_value(Q, key, game_data) for key in next_Q_keys]
	max_next_Q_value = max(next_Q_values)
	# Get new Q value
	new_Q_value = old_Q_value + learning_rate * (reward + discount_factor * max_next_Q_value - old_Q_value)
	Q[old_Q_key] = new_Q_value

# Create a Q dictionary, with keys matching to states
Q = {}

# Set some variables
learning_rate = 0.5#0.1
discount_factor = 0.0#0.9

scores = [0, 0, 0, 0]
for game_num in range(1, 10000001):

	#print(game_num)
	if game_num % 1000 == 0:
		print('#{} - {}'.format(game_num, scores))
		scores = [0, 0, 0, 0]

	# Game setup
	players, game_data = set_up_game(game_num, show_play=False)

	# First trick
	trick = start_trick(players, game_data)
	old_state = get_state(trick, players, game_data)
	action = get_player0_choice(players, game_data, trick, Q)
	player0_points = finish_trick(players, game_data, trick, action)
	reward = get_reward(player0_points)

	# Play game out
	while players[0].hand:
		# Get state
		trick = start_trick(players, game_data)
		new_state = get_state(trick, players, game_data)
	
		# Update Q
		if not game_data['first_trick']:
			update_Q(Q, old_state, action, learning_rate, reward, discount_factor, new_state, game_data)
	
		# Use Q to pick greedy choice
		player0_choice = get_player0_choice(players, game_data, trick, Q)
	
		# Get next state
		player0_points = finish_trick(players, game_data, trick, player0_choice)
	
		# Get reward
		reward = get_reward(player0_points)
	
		# Move new state to old state
		old_state = new_state

	# Show final scores
	#show_final_scores(players)
	reset_player_order(players)
	for i, player in enumerate(players):
		scores[i] += player.points
	#print(scores)
	







