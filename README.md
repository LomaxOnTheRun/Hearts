# Hearts

This is a project that will attempt to use reinforcement learning and neural networks to learn how to play the card game hearts.

### Next steps

Next few steps for project are:
- Add tests
 - Make sure that correct number of wins are happening for certain sets of starting cards
- Install Keras
- Add some NN capabilities and tests

### Assumptions

Current assumptions / changes to the rules made to simplify the gameplay:
- No shooting for the moon
- No passing card across the table from each other
- Variable number of players (as few as 2 players)
- Subsets of the full deck can be used (as few as 2 cards per player)

### display_utils.py

*NOTE*: The 'display_utils.py' file was for an initial attempt to read the screen of Ubuntu's Hearts program in order to play it. It was extremely slow at playing even a single game (a few seconds per game) and the complexity of the game could not be turned down sufficiently, so I opted to simply create a python framework for the game myself (now in game.py). This original attempt made the following assumptions:
- Using Ubuntu 16.04
- Using the Hearts game that comes as standard
- Using original sized window
- Set the background of the game to uniform green (b'\x00\xff\x00')
