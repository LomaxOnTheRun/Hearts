from game import *
from q_learning import *

from sys import stdout
from itertools import permutations

# NOTES:
# - I'm not shooting the moon for now (more complex), when I do:
#   - Need to think of how to reward / punish (-26*4 points at end?)
#   - Keep track of more history (other player scores / previously tricks)
# - I'm not passing cards across at the start of hands (more complex)



# FUTURE THOUGHTS:
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
		players = set_up_game(hand_num, game)
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

	if game.show_final_Q:
		show_Q(Q, model, game)
	
	if game.show_final_scores:
		show_final_scores(game)
	
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
	# Split cards into player hands
	game.num_hands = 1
	game.greediness = 1.0
	card_orders = permutations(game.get_deck_codes())
	num_cards = len(game.deck)
	cards_per_hand = num_cards / num_players
	assert cards_per_hand % 1 == 0
	cards_per_hand = int(cards_per_hand)
	for card_order in card_orders:
		hands_list = []
		for i in range(0, num_cards, cards_per_hand):
			hands_list.append(card_order[i:i+cards_per_hand])
		game.set_hands(hands_list)
		# Run game without learning
		run_game(game, do_learning=False)
	show_final_scores(game)


game = Game(num_players=2, num_hands=1000)
#game.show_play = True
#game.show_Q_values = True
#game.show_NN_values = True
#game.show_final_Q = True
game.show_running_scores = True

# Run game to learn
model = create_network_model(game)
Q, model, game = run_game(game)

# Run game to test model
#test_model(10000, game)
test_model_2(game)

# NOTE: For P2 always playing lowest value, P1 should get 38.33% of points -> model can get 36.67%...
#       For P2 always playing highest value, P1 should get 48.33% of points
# These values have been calculated by hand




