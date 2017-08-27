from display_utils import *
from game import *

# NOTES:
# - I'm not shooting the moon for now (more complex), when I do:
#   - Need to think of how to reward / punish
#   - Keep track of more history (other player scores / previously tricks)
# - I'm not passing cards across at the start of hands (more complex)


def do_player0_turn(players, game_data, trick):
	"""Lets you play your card"""
	player0 = get_player(players, 0)
	#player0_card_code = input('This is your hand:\n{}\nCard to play: '.format(player0.get_hand_codes()))
	card_code = player0.get_random_legal_card_to_play(trick, game_data)
	card = player0.play(card_code)
	trick.append(card)


# Game setup
players, game_data = set_up_game()

# Play game out
while players[0].hand:
	trick = start_trick(players, game_data)
	do_player0_turn(players, game_data, trick)
	finish_trick(players, game_data, trick)

# Show final scores
show_final_scores(players)











