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



def run_game(game, do_learning=True):
	"""
	Runs the game with metadata stored in 'game' for a number of hands equal to num_hands
	"""
	# Create a Q dictionary, with keys matching to states
	Q = {}
	
	new_percentage = False
	current_percentage = 0
	for hand_num in range(game.num_hands):
		# Hand counter
		hand_percentage = int((hand_num * 100.0) / game.num_hands) + 1
		if hand_percentage > current_percentage:
			new_percentage = True
			stdout.write('{}Running games [{}%]'.format('\b'*20, hand_percentage))
			stdout.flush()

		# Game setup
		players = set_up_game(game)
		if game.hands_list:
			players = game.set_hands(game.hands_list)
				
	
		# Show cumulative scores per X number of games
		if game.show_scores and hand_num % 10000 == 0:
			print('\n#{} - {}'.format(hand_num, game.cumulative_scores))
			game.cumulative_scores = [0] * num_players

		# First trick
		trick = start_trick(players, game)
		old_state_str = get_state_str(trick, players, game)
		action = get_player0_choice(players, game, trick, Q, model)
		player0_points = finish_trick(players, game, trick, action)
		reward = get_reward(player0_points)
		if game.show_Q_values:
			print(action + ' = ' + str(reward) + ' points')

		# Play game out
		while players[0].hand:
			# Get state
			trick = start_trick(players, game)
			new_state_str = get_state_str(trick, players, game)
	
			# Update Q
			if not game.first_trick:
				player0 = get_player(players, 0)
				legal_moves = player0.get_legal_moves(trick, game)
				if do_learning:
					update_Q(
						Q,
						old_state_str,
						action,
						reward,
						new_state_str,
						game,
						legal_moves,
						model
					)
	
			# Use Q to pick greedy choice
			action = get_player0_choice(players, game, trick, Q, model)
	
			# Get next state
			player0_points = finish_trick(players, game, trick, action)
	
			# Get reward
			reward = get_reward(player0_points)
			if game.show_Q_values:
				print(action + ' = ' + str(reward) + ' points')
	
			# Move new state to old state
			old_state_str = new_state_str
	
		# Do final learning
		if do_learning:
			update_Q(
				Q,
				old_state_str,
				action,
				reward,
				'terminal',
				game,
				legal_moves,
				model
			)

		# Show final scores
		reset_player_order(players)
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
			percentage_points = test_model_3(game)
			game.percentage_points.append(percentage_points)

	if game.show_final_Q:
		show_Q(Q, model, game)
	
	if game.show_final_scores:
		show_final_scores(game)
	
	# Do final assessment and show total
	percentage_points = test_model_3(game)
	game.percentage_points.append(percentage_points)
	print('\n', game.percentage_points, '\n')
	
	return Q, model, game


def test_model(num_hands, game):
	"""Runs a random number of games with full greediness"""
	print('\n#################\n#   Test runs   #\n#################\n')
	# Reset scores
	game.hand_num = 0
	game.cumulative_scores = [0] * game.num_players
	game.hands_won = [0] * game.num_players
	game.points_won = [0] * game.num_players
	game.show_running_scores = False
	# Run game without learning
	game.num_hands = num_hands
	game.greediness = 1.0
	run_game(game, do_learning=False)


def test_model_2(game):
	"""Runs every possible combination of cards for every player, with full greediness"""
	print('\n#################\n#   Test runs   #\n#################\n')
	print('Testing all possible hand combinations...')
	# Reset scores
	num_players = game.num_players
	game.hand_num = 0
	game.cumulative_scores = [0] * num_players
	game.hands_won = [0] * num_players
	game.points_won = [0] * num_players
	game.show_running_scores = False
	game.show_final_scores = False
	# Make game network as well as possible
	game.num_hands = 1
	game.greediness = 1.0
	# Calculate number of cards per hand
	num_cards = len(game.deck)
	cards_per_hand = num_cards / num_players
	assert cards_per_hand % 1 == 0
	cards_per_hand = int(cards_per_hand)
	# Get a unique set of all card combinations possible
	card_orders_all = permutations(game.get_deck_codes())
	card_orders = get_all_unique_combinations(card_orders_all, cards_per_hand)
	# Keep track of points won for every hand
	points_won_for_hand = []
	for card_order in card_orders:
		game.points_won = [0] * num_players
		# Split cards into player hands
		hands_list = []
		for i in range(0, num_cards, cards_per_hand):
			hands_list.append(card_order[i:i+cards_per_hand])
		game.set_hands(hands_list)
		# Run game without learning
		run_game(game, do_learning=False)
		points_won_for_hand.append((hands_list, game.points_won))
	show_final_scores(game)
	return points_won_for_hand


def test_model_3(game):
	"""Runs all unique combinations of hands once with greedy network, returns single percentage points value"""
	# Calculate number of cards per hand
	num_cards = len(game.deck)
	cards_per_hand = int(num_cards / game.num_players)
	# Get a unique set of all card combinations possible
	card_sets_all = permutations(game.get_deck_codes())
	card_sets = get_all_unique_combinations(card_sets_all, cards_per_hand)
	#print(card_orders)
	# Split cards into player hands
	hands_list = split_card_set_into_hands(card_sets, num_cards, cards_per_hand)
	# Run a single hand for each hand set
	total_points = [0] * game.num_players
	for hand_list in hands_list:
		points = run_single_greedy_hand(game.num_players, hand_list)
		total_points = [sum(x) for x in zip(total_points, points)]
	percentage_points = get_percentage_points(total_points)
	return percentage_points


def split_card_set_into_hands(card_sets, num_cards, cards_per_hand):
	"""Split a set of cards into tuples of hands"""
	hands_list = []
	for card_set in card_sets:
		hand_list = []
		for i in range(0, num_cards, cards_per_hand):
			hand_list.append(card_set[i:i+cards_per_hand])
		hands_list.append(hand_list)
	return hands_list


def run_single_greedy_hand(num_players, hands_list):
	"""Run a single hand with no learning, returns points"""
	Q = {}
	game = Game(num_players=num_players, greediness=1.0, num_hands=1)
	players = set_up_game(game)
	players = game.set_hands(hands_list)
	trick = start_trick(players, game)
	action = get_player0_choice(players, game, trick, Q, model)
	player0_points = finish_trick(players, game, trick, action)
	while players[0].hand:
		trick = start_trick(players, game)
		action = get_player0_choice(players, game, trick, Q, model)
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




game = Game(num_players=2, num_hands=100000)
#game.show_play = True
#game.show_Q_values = True
#game.show_NN_values = True
#game.show_final_Q = True
#game.show_running_scores = True
#game.show_points_won_per_hand = True

# Run game to learn
model = create_network_model(game)
Q, model, game = run_game(game)

# Show graph of points earned
show_percentage_points_graph(game)

# Run game to test model
#test_model(10000, game)
#points_won_for_hand = test_model_2(game)

#if game.show_points_won_per_hand:
#	show_best_score_for_hands(points_won_for_hand)

# NOTE: For P2 always playing lowest value, P1 should get 36.67% of the points
#       For P2 always playing highest value, P1 should get 48.33% of the points
# These values have been calculated by hand
#
# For 2 players, 4 cards each, lowest card, fewest % of points is 33.21%
#  - 10000 not enough, 100000 enough




