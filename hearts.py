from game import *
from q_learning import *

from sys import stdout
from itertools import permutations

import matplotlib.pyplot as plt

# NOTES:
# - I'm not shooting the moon for now (more complex), when I do:
#   - Need to think of how to reward / punish (-26*4 points at end?)
#   - Keep track of more history (other player scores / previously tricks)
# - I'm not passing cards across at the start of hands (more complex)



# FUTURE THOUGHTS:
# - REMOVE Q?
# - CALCULATE BY HAND BEST ODDS OF WINNING WITH SUBSET OF CARDS, SEE HOW CLOSE NET GETS
# - TRAIN NETWORK WITH SUBSETS OF CARDS, AND EXPAND TO FILL ARRAYS WITH ZEROS



def run_game(game, run_tests=False):
	"""
	Runs the game with metadata stored in 'game' for a number of hands equal to num_hands
	"""
	new_percentage = False
	current_percentage = 0
	for hand_num in range(game.num_hands):
		# Hand counter
		hand_percentage = int((hand_num * 100.0) / game.num_hands) + 1
		if hand_percentage > current_percentage:
			new_percentage = True
			stdout.write('{}Running games [{}%]'.format('\b'*20, hand_percentage))
			stdout.flush()

		# Show cumulative scores per X number of games
		show_cummulative_scores(game, hand_num)

		# Game setup
		players = set_up_game(game)
		if game.hands_list:
			players = game.set_hands(game.hands_list)

		# This gets set after first hand
		old_state_str = None

		# Play game
		while players[0].hand:
			# Get state
			trick = start_trick(players, game)
			new_state_str = get_state_str(trick, players, game)

			# Update Q
			if old_state_str:  # And therefore not first trick
				player0 = get_player(players, 0)
				legal_moves = player0.get_legal_moves(trick, game)
				update_Q(
					old_state_str,
					action,
					reward,
					new_state_str,
					game,
					legal_moves,
					model
				)

			# Use Q to pick greedy choice
			action = get_player0_choice(players, game, trick, model)

			# Get next state
			player0_points = finish_trick(players, game, trick, action)

			# Get reward
			reward = get_reward(player0_points)
			if game.show_Q_values:
				print(action + ' = ' + str(reward) + ' points')

			# Move new state to old state
			old_state_str = new_state_str

		# Do final learning
		update_Q(
			old_state_str,
			action,
			reward,
			'terminal',
			game,
			legal_moves,
			model
		)

		# This keeps learning player at start
		reset_player_order(players)

		# Update cummulative scores
		for i, player in enumerate(players):
			game.cumulative_scores[i] += player.points

		# Get winners for current game
		points = [player.points for player in players]
		game.update_points_won(points)
		min_points = min(points)
		winners = [index for index, point in enumerate(points) if point == min_points]
		for winner in winners:
			game.hands_won[winner] += 1

		if game.show_running_scores and new_percentage:
			row_format = '{:>15}' * game.num_players
			print(row_format.format(*game.points_won))
			game.points_won = [0] * game.num_players

		if new_percentage:
			current_percentage = hand_percentage
			new_percentage = False
			if run_tests:
				percentage_points = test_model(game)
				game.percentage_points.append(percentage_points)

	if game.show_final_Q:
		show_Q(model, game)

	if game.show_final_scores:
		show_final_scores(game)

	if run_tests:
		# Do final assessment and show total
		percentage_points = test_model(game)
		game.percentage_points.append(percentage_points)
		print('\n', game.percentage_points, '\n')

	return model, game


def test_model(game):
	"""Runs all unique combinations of hands once with greedy network, returns single percentage points value"""
	# Run a single hand for each hand set
	total_points = [0] * game.num_players
	for hand_codes in game.unique_hand_codes:
		points = run_single_greedy_hand(game.num_players, hand_codes)
		total_points = [sum(x) for x in zip(total_points, points)]
	percentage_points = get_percentage_points(total_points)
	return percentage_points


def run_single_greedy_hand(num_players, hand_codes):
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


def show_percentage_points_graph(game):
	num_points = len(game.percentage_points)
	x_step = int(game.num_hands / (num_points - 1))
	x = range(0, game.num_hands+1, x_step)
	y = game.percentage_points
	plt.plot(x, y)
	plt.ylabel('% of points gained')
	plt.xlabel('Number of hands played')
	plt.title('% points earned by Player 0 ({} total players)\n' \
			  'Deck: {}'.format(game.num_players, game.get_deck_codes()))
	plt.show()




game = Game(num_players=2, num_hands=10000)
profile_game = False
#game.show_play = True
#game.show_Q_values = True
#game.show_final_Q = True
#game.show_running_scores = True
#game.show_points_won_per_hand = True

# Create neural network
model = create_network_model(game)

# Run game
if profile_game:
	import cProfile
	cProfile.run('run_game(game)')
else:
	model, game = run_game(game, run_tests=True)
	# Show graph of points earned
	if game.percentage_points:
		show_percentage_points_graph(game)

#if game.show_points_won_per_hand:
#	show_best_score_for_hands(points_won_for_hand)

# NOTE: For P2 always playing lowest value, P1 should get 36.67% of the points
#       For P2 always playing highest value, P1 should get 48.33% of the points
# These values have been calculated by hand
#
# For 2 players, 4 cards each, lowest card, fewest % of points is 33.21%
#  - 10000 not enough, 100000 enough
