from random import shuffle, randint, choice


#SUITS = ['C', 'D', 'S', 'H']
#VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

SUITS = ['H']
VALUES = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


class Card:
	def __init__(self, suit, value_str):
		self.suit = suit
		self.value = self.get_value(value_str)
		self.code = suit + value_str
		self.points = self.get_points()
		self.sort_value = 100 * SUITS.index(suit) + VALUES.index(value_str)
	
	def get_value(self, value_str):
		royals = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
		if value_str in royals:
			return royals[value_str]
		else:
			return int(value_str)
	
	def get_points(self):
		if self.code == 'SQ':
			return 13
		elif self.suit == 'H':
			return 1
		else:
			return 0


class Player:
	def __init__(self, id_val):
		self.id_val = id_val
		self.points = 0
		self.hand = []
		self.lead = False
	
	def get_hand_codes(self):
		return [card.code for card in self.hand]
	
	def play(self, card_code):
		for index, card in enumerate(self.hand):
			if card.code == card_code:
				self.lead = False
				return self.hand.pop(index)
	
	def get_legal_moves(self, trick, game):
		hand_codes = self.get_hand_codes()
		# If lead
		if self.lead:
			# Lead with C2 as first card of game
			if game.first_trick:
				#return ['C2']
				return [SUITS[0] + VALUES[0]]
			# If hearts are broken, play whatever
			elif game.hearts_broken:
				return hand_codes
			# Or if you only have hearts, play whatever
			elif all([code[0] == 'H' for code in hand_codes]):
				return hand_codes
			# If hearts are unbroken, play anything else
			else:
				return [code for code in hand_codes if code[0] is not 'H']
		# Else try to follow suit
		else:
			lead_card = trick[0]
			legal_moves = [code for code in hand_codes if code[0] is lead_card.suit]
			# Don't play queen on first move
			if game.first_trick and 'SQ' in legal_moves:
				legal_moves.remove('SQ')
			# If can't follow suit, play whatever
			if not legal_moves:
				return hand_codes
			return legal_moves
	
	def get_random_legal_card_to_play(self, trick, game):
		legal_moves = self.get_legal_moves(trick, game)
		if not legal_moves:
			print([card.code for card in trick])
			print(self.get_hand_codes())
		card_to_play = choice(legal_moves)
		return card_to_play
	
	def sort_hand(self):
		sort_values = [card.sort_value for card in self.hand]
		while sort_values:
			min_index = sort_values.index(min(sort_values))
			self.hand.append(self.hand.pop(min_index))
			del sort_values[min_index]


class Game:
	"""This keeps all the game metadata"""
	def __init__(self, num_players=4, num_hands=1000, show_play=False, show_Q_values=False, show_scores=False, show_final_Q=False):
		# User selected info
		self.num_players = num_players
		self.num_hands = num_hands
		# Cumulative record
		self.hand_num = 0
		self.cumulative_scores = [0] * num_players
		self.hands_won = [0] * num_players
		# Switches that get reset every hand
		self.first_trick = True
		self.hearts_broken = False
		# Debug options
		self.show_play = show_play
		self.show_Q_values = show_Q_values
		self.show_scores = show_scores
		self.show_final_Q = show_final_Q


def set_up_game(game_num, num_players):
	players = shuffle_and_deal_cards(num_players)
	set_first_lead(players)
	return players


def start_trick(players, game):
	"""Start trick, including prep"""
	put_players_in_turn_order(players)
	players_before, _, _ = split_players(players)
	trick = play_trick_for_players(players_before, game, [])
	return trick


def finish_trick(players, game, trick, player0_choice):
	"""Finish trick including points and next lead"""
	_, player0, players_after = split_players(players)
	player0_card = player0.play(player0_choice)
	trick.append(player0_card)
	trick = play_trick_for_players(players_after, game, trick)
	update_hearts_broken(game, trick)
	player0_points = give_trick_points(players, trick)
	if game.show_play:
		print('Trick: {}\n'.format([card.code for card in trick]))
	game.first_trick = False
	return player0_points


def shuffle_and_deal_cards(num_players):
	"""Shuffle and deal cards"""
	players = [Player(i) for i in range(num_players)]
	deck = [Card(suit, value_str) for suit in SUITS for value_str in VALUES]
	shuffle(deck)
	hand_size = int((len(SUITS) * len(VALUES)) / num_players)
	for player in players:
		player.hand = deck[:hand_size]
		del deck[:hand_size]
		player.sort_hand()
	return players


def set_first_lead(players):
	"""Find first player to start game with C2"""
	for player in players:
		#if 'C2' in player.get_hand_codes():
		lowest_card = SUITS[0] + VALUES[0]
		if lowest_card in player.get_hand_codes():
			player.lead = True
			break


def put_players_in_turn_order(players):
	"""Put players in correct turn order"""
	while players[0].lead == False:
		players.append(players.pop(0))


def get_player(players, id_val):
	"""Return player with specified id_val"""
	for player in players:
		if player.id_val == id_val:
			return player


def split_players(players):
	"""Split players into those before you, you, and after you"""
	player0 = get_player(players, 0)
	player0_index = players.index(player0)
	players_before = players[:player0_index]
	players_after = players[player0_index+1:]
	return players_before, player0, players_after


def play_trick_for_players(players, game, trick):
	"""Play the trick for a subgroup of players"""
	for player in players:
		# For now, play randomly
		card_to_play = player.get_random_legal_card_to_play(trick, game)
		if game.show_play:
			print(card_to_play + ' ' + str(player.get_hand_codes()))
		card = player.play(card_to_play)
		trick.append(card)
	return trick


def update_hearts_broken(game, trick):
	"""Check if hearts have been broken"""
	if not game.hearts_broken:
		for card in trick:
			if card.suit is 'H':
				game.hearts_broken = True


def give_trick_points(players, trick):
	"""Give winner of trick points and the lead, return player0 points"""
	winner = 0
	lead_suit = trick[0].suit
	max_value = 0
	for index, card in enumerate(trick):
		if card.value > max_value:
			max_value = card.value
			winner = index
	points = sum([card.points for card in trick])
	players[winner].points += points
	players[winner].lead = True
	if players[winner].id_val == 0:
		return points
	else:
		return 0


def reset_player_order(players):
	while players[0].id_val is not 0:
		players.append(players.pop(0))


def show_final_scores(players):
	"""Print out final scores"""
	reset_player_order(players)
	print('Final scores:')
	for player in players:
		print('player{} - {}'.format(player.id_val, player.points))


###################
#   DEBUG UTILS   #
###################


def show_hands(players):
	for player in players:
		print('player{} - {}'.format(player.id_val, player.get_hand_codes()))


def set_hands(hands_list):
	"""
	Takes a list of list of card codes for values
	
	e.g. [['H2', 'H3'],  # Player 0
		  ['H4', 'H5']]  # Player 1
	"""
	players = [Player(i) for i in range(len(hands_list))]
	for index, hand in enumerate(hands_list):
		player = players[index]
		player.hand = []
		for card_str in hand:
			card = Card(card_str[0], card_str[1:])
			player.hand.append(card)
	set_first_lead(players)
	return players






