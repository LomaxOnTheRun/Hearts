from q_learning import *
from game import *

from time import time
from keras.models import model_from_json

# NOTES:
# - I'm not shooting the moon for now (more complex), when I do:
#   - Need to think of how to reward / punish (-26*4 points at end?)
#   - Keep track of more history (other player scores / previously tricks)
# - I'm not passing cards across at the start of hands (more complex)
#   - Once main network trained, could train secondary network for this

# FUTURE THOUGHTS:
# - ADD DECORATORS TO TIME FUNCTIONS
# - TRY PLAYING WITH 3+ PLAYERS
# - ADD Learner OBJECT FOR Q-LEARNING / NEURAL NETWORK
# - SHOW NEWTORK STRUCTURE ON GRAPHS
# - TRAIN NETWORK WITH SUBSETS OF CARDS, AND EXPAND TO FILL ARRAYS WITH ZEROS
# - LOOK INTO COMBINING LAST 2 SETS OF INPUTS (+1 FOR PLAYED, -1 FOR KEPT IN HAND)
# - TRY MULTIPLE HIDDEN LAYERS
# - LOOK INTO OTHER OPTIMISATIONS (E.G. L1 / L2)
# - PRACTICE ON RUNS IT FAILS AT


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


def get_model_name(model, game):
	"""Get name of save files from game and model structure"""

	# Add game info
	name_sections = [f'{game.num_players}P']
	name_sections.append(''.join(SUITS))
	name_sections.append(''.join(VALUES))

	for layer in model.get_config():
		layer_type = layer['config']['name'].split('_')[0]
		layer_size = layer['config']['units']
		activation = layer['config']['activation']
		name_sections.append(f'{layer_type}{layer_size}{activation}')

	return '_'.join(name_sections)


def save_model(model, game):
	name = get_model_name(model, game)
	model_json = model.to_json()
	with open(f'model_saves/{name}.json', 'w') as json_file:
		json_file.write(model_json)
	model.save_weights(f'model_saves/{name}.h5')
	print('Model saved')


def load_model(model):
	name = get_model_name(model, game)
	try:
		json_file = open(f'model_saves/{name}.json', 'r')
		loaded_model_json = json_file.read()
		json_file.close()
		model = model_from_json(loaded_model_json)
		model.load_weights(f'model_saves/{name}.h5')
		print('Model loaded')
	except FileNotFoundError:
		print(f'No pre-existing model found for {name!r},' \
		 	   ' using newly created model instead')

	return model


game = Game(num_players=2, num_hands=100)
profile_game = False
game.run_assessment_tests = True
#game.show_final_Q = True
#use_previous_model = True

# Create neural network
optimizer='sgd'
loss='mse'

model = create_network_model(game, optimizer=optimizer, loss=loss)
if 'use_previous_model' in locals() and use_previous_model:
	model = load_model(model)
	model.compile(optimizer=optimizer, loss=loss)


# Run game
if profile_game:
	import cProfile
	cProfile.run('run_game(game)')
else:
	start_time = time()
	game, model = run_game(game)
	print('Time taken: %0.1fs' % (time() - start_time))
	# Show graph of points earned
	if game.percentage_points:
		show_percentage_points_graph(game)
	# Save model
	# save_model(model, game)
