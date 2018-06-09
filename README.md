# Hearts

This is a project that will attempt to use reinforcement learning and neural networks to learn how to play the card game hearts.

### Assumptions

Current assumptions / changes to the rules made to simplify the gameplay:
- No shooting for the moon
- No passing card across the table from each other
- Variable number of players (as few as 2 players)
- Subsets of the full deck can be used (as few as 2 cards per player)

### Reinforcement Learning

I'm using SARSA as my reinforcement learning front end. This means that:
 - The game is played until it's the agent's turn
 - The agent then has its current state
   - This is *current hand* and *current trick*
 - The network learns
   - See *Updating the Q-values and Neural Network*
 - The agent chooses an action
   - Currently a mostly-greedy choice based on Q values
 - The rest of the trick is played out
 - The reward is calculated

### Updating the Q-values and Neural Network

Once a new state has been found:
 - Work out *best* possible Q value for current state/action pair
 - Uses this value, plus any rewards, to recalculate the Q value for the previous state/action pair
 - Use this new value of the previous state/action pair to train the neural network once

### Neural Network

This is currently a very basic network with:
 - 156 input nodes
   - 52 to represent the cards in the agent's hand
   - 52 to represent the cards already in the trick
   - 52 to represent the card being played
 - A single hidden layer with 200 nodes
 - A single output node

 I'm using MSE to calculate the error and SGD as my learning algorithm, but only because I haven't tried anything else yet.

### display_utils.py

*NOTE*: The 'display_utils.py' file was for an initial attempt to read the screen of Ubuntu's Hearts program in order to play it. It was extremely slow at playing even a single game (a few seconds per game) and the complexity of the game could not be turned down sufficiently, so I opted to simply create a python framework for the game myself (now in game.py). This original attempt made the following assumptions:
- Using Ubuntu 16.04
- Using the Hearts game that comes as standard
- Using original sized window
- Set the background of the game to uniform green (b'\x00\xff\x00')
