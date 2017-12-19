import pytest

from hearts import *


def test_hands_won():
	"""Check Q learning gets at least 99% wins with simple preset hands"""
	game = Game(num_players=2, num_hands=10000)
	hands_list = [['S10', 'SQ'], ['DJ', 'SK']]
	Q, game = run_game(game, hands_list)
	assert game.hands_won[0] > float(game.num_hands) * 0.99


def test_incorrect_hands_list():
	"""Check exception occures if hands_list doesn't match to num_players"""
	game = Game(num_players=4, num_hands=1)
	hands_list = [['S10', 'SQ'], ['DJ', 'SK']]
	with pytest.raises(Exception) as e:
		Q, game = run_game(game, hands_list)
	assert 'Set hands list not equal to set number of players in game' in str(e.value)
