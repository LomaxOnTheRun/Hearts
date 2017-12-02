from game import *
from q_learning import *

from random import randint


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
	state_str = get_state_str(trick, players, game_data)
	Q_keys = [get_Q_key(state_str, move) for move in legal_moves]
	Q_values = [get_Q_value(Q, key) for key in Q_keys]
	if game_data['show_Q_values']:
		for i in range(len(Q_keys)):
			print('{} -> {}'.format(Q_keys[i], Q_values[i]))
	max_Q_value = max(Q_values)
	best_moves = []
	for index, value in enumerate(Q_values):
		if value == max_Q_value:
			best_moves.append(legal_moves[index])
	chosen_move = choice(best_moves)
	return chosen_move


def show_hands(players):
	for player in players:
		print('player{} - {}'.format(player.id_val, player.get_hand_codes()))


# Create a Q dictionary, with keys matching to states
Q = {}

# Set some variables
num_players = 2
learning_rate = 0.5#0.1
discount_factor = 0.9

num_games = 10000
scores = [0 for player in range(num_players)]
games_won = [0 for player in range(num_players)]
for game_num in range(num_games):
	
	# Game setup
	players, game_data = set_up_game(game_num, num_players)
	
#	test_hands = [['H3', 'H5'],
#				  ['H4', 'H6']]
#	if randint(0, 1) == 1:
#		test_hands.reverse()
#	players = set_hands(test_hands)
	
#	game_data['show_Q_values'] = True
#	game_data['show_play'] = True
#	show_hands(players)
#	print(game_num)
	
#	if game_num % 10000 == 0:
#		print('\n#{} - {}'.format(game_num, scores))
#		scores = [0, 0, 0, 0]
#	else:
#		game_data['show_Q_values'] = False

	# First trick
	trick = start_trick(players, game_data)
	old_state_str = get_state_str(trick, players, game_data)
	action = get_player0_choice(players, game_data, trick, Q)
	player0_points = finish_trick(players, game_data, trick, action)
	reward = get_reward(player0_points)
	if game_data['show_Q_values']:
		print(action + ' = ' + str(reward) + ' points')

	# Play game out
	while players[0].hand:
		# Get state
		trick = start_trick(players, game_data)
		new_state_str = get_state_str(trick, players, game_data)
	
		# Update Q
		if not game_data['first_trick']:
			player0 = get_player(players, 0)
			legal_moves = player0.get_legal_moves(trick, game_data)
			update_Q(Q, old_state_str, action, learning_rate, reward, discount_factor, new_state_str, game_data, legal_moves)
	
		# Use Q to pick greedy choice
		action = get_player0_choice(players, game_data, trick, Q)
	
		# Get next state
		player0_points = finish_trick(players, game_data, trick, action)
	
		# Get reward
		reward = get_reward(player0_points)
		if game_data['show_Q_values']:
			print(action + ' = ' + str(reward) + ' points')
	
		# Move new state to old state
		old_state_str = new_state_str
	
	# Do final learning
	update_Q(Q, old_state_str, action, learning_rate, reward, discount_factor, 'terminal', game_data, legal_moves)

	# Show final scores
	#show_final_scores(players)
	reset_player_order(players)
	for i, player in enumerate(players):
		scores[i] += player.points
	
	winner = scores.index(min(scores))
	games_won[winner] += 1	
	
	if game_num == num_games - 1:
		print(scores)
		print(games_won)


show_Q(Q)




