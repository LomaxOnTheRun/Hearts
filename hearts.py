from q_learning import *
from game import *

# NOTES:
# - I'm not shooting the moon for now (more complex), when I do:
#   - Need to think of how to reward / punish (-26*4 points at end?)
#   - Keep track of more history (other player scores / previously tricks)
# - I'm not passing cards across at the start of hands (more complex)
#   - Once main network trained, could train secondary network for this

# FUTURE THOUGHTS:
# - TRY PLAYING WITH 3+ PLAYERS
# - ADD Learner OBJECT FOR Q-LEARNING / NEURAL NETWORK
# - SHOW NEWTORK STRUCTURE ON GRAPHS
# - TRAIN NETWORK WITH SUBSETS OF CARDS, AND EXPAND TO FILL ARRAYS WITH ZEROS
# - LOOK INTO COMBINING LAST 2 SETS OF INPUTS (+1 FOR PLAYED, -1 FOR KEPT IN HAND)
# - TRY MULTIPLE HIDDEN LAYERS
# - LOOK INTO OTHER OPTIMISATIONS (E.G. L1 / L2)


def play_hand(game, model):
	# Game setup
	players = set_up_game(game)
	old_state_str = None

	# Play game
	while players[0].hand:
		trick = start_trick(players, game)
		new_state_str = get_state_str(trick, players, game)

		# Update Q
		if old_state_str:  # And therefore not first trick
			player0 = get_player(players, 0)
			legal_moves = player0.get_legal_moves(trick, game)
			update_Q(old_state_str, action, reward, new_state_str, game, legal_moves, model)

		action = get_player0_choice(players, game, trick, model)
		player0_points = finish_trick(players, game, trick, action)
		reward = get_reward(player0_points)
		old_state_str = new_state_str

		if game.show_Q_values:
			print(action + ' = ' + str(reward) + ' points')

	update_Q(old_state_str, action, reward, 'terminal', game, None, model)
	reset_player_order(players)

	return players


def run_game(game):
	"""Runs the game with metadata stored in 'game'"""
	for hand_num in range(game.num_hands):
		do_pre_hand_logging(game, hand_num)
		players = play_hand(game, model)
		do_post_hand_logging(game, model, players, hand_num, test_model)
	do_post_game_logging(game, model, test_model)

	return game, model


game = Game(num_players=3, num_hands=10)
profile_game = False
game.run_assessment_tests = True
#game.show_final_Q = True

# Create neural network
model = create_network_model(game)

# Run game
if profile_game:
	import cProfile
	cProfile.run('run_game(game)')
else:
	game, model = run_game(game)
	# Show graph of points earned
	if game.percentage_points:
		show_percentage_points_graph(game)
