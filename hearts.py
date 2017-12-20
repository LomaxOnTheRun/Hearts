from game import *
from q_learning import *

from sys import stdout


# NOTES:
# - I'm not shooting the moon for now (more complex), when I do:
#   - Need to think of how to reward / punish (-26*4 points at end?)
#   - Keep track of more history (other player scores / previously tricks)
# - I'm not passing cards across at the start of hands (more complex)

def run_game(game, hands_list=None):
	"""
	Runs the game with metadata stored in 'game' for a number of hands equal to num_hands
	"""
	# Create a Q dictionary, with keys matching to states
	Q = {}
	
	current_percentage = 0
	for hand_num in range(game.num_hands):
		# Hand counter
		hand_percentage = int((hand_num * 100.0) / game.num_hands) + 1
		if hand_percentage > current_percentage:
			current_percentage = hand_percentage
			stdout.write('{}Running games [{}%]'.format('\b' * 20, current_percentage))
			stdout.flush()

		# Game setup
		players = set_up_game(hand_num, game)
		if hands_list:
			players = set_hands(hands_list, game)
	
		# Show cumulative scores per X number of games
		if game.show_scores and hand_num % 10000 == 0:
			print('\n#{} - {}'.format(hand_num, game.cumulative_scores))
			game.cumulative_scores = [0] * num_players

		# First trick
		trick = start_trick(players, game)
		old_state_str = get_state_str(trick, players, game)
		action = get_player0_choice(players, game, trick, Q)
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
				update_Q(
					Q,
					old_state_str,
					action,
					reward,
					new_state_str,
					game,
					legal_moves
				)
	
			# Use Q to pick greedy choice
			action = get_player0_choice(players, game, trick, Q)
	
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
			Q,
			old_state_str,
			action,
			reward,
			'terminal',
			game,
			legal_moves
		)

		# Show final scores
		#show_final_scores(players)
		reset_player_order(players)
		for i, player in enumerate(players):
			game.cumulative_scores[i] += player.points
	
		# Get winners for current game
		points = [player.points for player in players]
		min_points = min(points)
		winners = [index for index, point in enumerate(points) if point == min_points]
		for winner in winners:
			game.hands_won[winner] += 1	
	
		if hand_num == game.num_hands - 1:
			print('\nCumulative scores:\t{}'.format(game.cumulative_scores))
			print('Hands won:\t\t{}'.format(game.hands_won))

	if game.show_final_Q:
		show_Q(Q)
	
	return Q, game


game = Game(num_players=2, num_hands=100000)
#game.show_play = True
#game.show_Q_values = True
game.show_final_Q = True

hands_list = [['SJ', 'SQ'], ['S10', 'SK']]
Q, game = run_game(game, hands_list)

