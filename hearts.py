from display_utils import *
from game import *

# NOTES:
# - I'm not shooting the moon for now (more complex), when I do:
#   - Need to think of how to reward / punish
#   - Keep track of more history (other player scores / previously tricks)
# - I'm not passing cards across at the start of hands (more complex)

# Set to true for logging
show_play = True

# Hearts have to be broken before they can be played
hearts_broken = False

players = shuffle_and_deal_cards()
set_first_lead(players)
put_players_in_turn_order(players)

# First trick
trick = play_trick(players, hearts_broken, first_trick=True, show_play=show_play)
hearts_broken = is_hearts_broken(trick)
give_trick_points(players, trick)
if show_play:
	print()

# Finish game
while players[0].hand:
	put_players_in_turn_order(players)
	trick = play_trick(players, hearts_broken, show_play=show_play)
	if not hearts_broken:
		hearts_broken = is_hearts_broken(trick)
	give_trick_points(players, trick)
	if show_play:
		print()

show_final_scores(players)











