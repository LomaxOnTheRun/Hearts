from hearts import *

def test_hands_won():
	game = Game(num_players=2, num_hands=10000)
	hands_list = [['S10', 'SQ'], ['DJ', 'SK']]
	Q, game = run_game(game, hands_list)
	assert game.hands_won[0] > float(game.num_hands) * 0.99
