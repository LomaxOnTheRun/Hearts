import pytest

from hearts import *


def test_hands_won():
	"""Check Q learning gets at least 99% wins with simple preset hands"""
	game = Game(num_players=2, num_hands=1)
	game.set_hands([['S10', 'SQ'], ['DJ', 'SK']])
	Q, game = run_game(game)
	assert game.hands_won[0] > float(game.num_hands) * 0.99


def test_incorrect_hands_list():
	"""Check exception occures if hands_list doesn't match to num_players"""
	game = Game(num_players=4, num_hands=1)
	hands_list = [['S10', 'SQ'], ['DJ', 'SK']]
	with pytest.raises(Exception) as e:
		Q, game = run_game(game, hands_list)
	assert 'Set hands list not equal to set number of players in game' in str(e.value)


def test_str_to_array_conversion():
	game = Game(num_hands=1)
	state_str = 'D3SJSQH2_C4D3_CKSK'
	binary_array = state_str_to_array(state_str, game)
	created_state_str = array_to_state_str(binary_array, game)
	assert state_str == created_state_str
