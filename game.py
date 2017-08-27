from random import shuffle, randint


SUITS = ['C', 'D', 'S', 'H']
VALUES = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']


class Card:
	def __init__(self, suit, value_str):
		self.suit = suit
		self.value = self.get_value(value_str)
		self.points = self.get_points()
		self.code = suit + value_str
	
	def get_value(self, value_str):
		royals = {'J': 11, 'Q': 12, 'K': 13, 'A': 14}
		if value_str in royals:
			return royals[value_str]
		else:
			return int(value_str)
	
	def get_points(self):
		if self.suit == 'S' and self.value == 12:
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
	
	def get_legal_moves(self, trick, hearts_broken, first_trick=False):
		hand_codes = self.get_hand_codes()
		# If lead
		if self.lead:
			# Lead with C2 as first card of game
			if first_trick:
				return ['C2']
			# If hearts are broken, play whatever
			elif hearts_broken:
				return hand_codes
			# If hearts are unbroken, play anything else
			else:
				return [code for code in hand_codes if code[0] is not 'H']
		# Else try to follow suit
		else:
			lead_card = trick[0]
			legal_moves = [code for code in hand_codes if code[0] is lead_card.suit]
			# If can't follow suit, play whatever
			if not legal_moves:
				return hand_codes
			return legal_moves


def shuffle_and_deal_cards():
	"""Shuffle and deal cards"""
	players = [Player(i) for i in range(4)]
	deck = [Card(suit, value_str) for suit in SUITS for value_str in VALUES]
	shuffle(deck)
	for player in players:
		player.hand = deck[:13]
		del deck[:13]
	return players

def set_first_lead(players):
	"""Find first player to start game with C2"""
	for player in players:
		if 'C2' in player.get_hand_codes():
			player.lead = True
			break

def put_players_in_turn_order(players):
	"""Put players in correct turn order"""
	while players[0].lead == False:
		players.append(players.pop(0))


def play_trick(players, hearts_broken, first_trick=False, show_play=False):
	trick = []
	for player in players:
		legal_moves = player.get_legal_moves(trick, hearts_broken, first_trick=first_trick)
		card_to_play = legal_moves[randint(0, len(legal_moves)-1)]  # For now, play randomly
		if show_play:
			print(card_to_play + ' ' + str(player.get_hand_codes()))
		card = player.play(card_to_play)
		trick.append(card)
	return trick

def is_hearts_broken(trick):
	"""Check if hearts have been broken"""
	for card in trick:
		if card.suit is 'H':
			return True
	return False

def give_trick_points(players, trick):
	"""Give winner of trick points and the lead"""
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

def show_final_scores(players):
	"""Print out final scores"""
	for player in players:
		if player.id_val == 0:
			player.lead = True
	put_players_in_turn_order(players)
	print('Final scores:')
	for player in players:
		print('player{} - {}'.format(player.id_val, player.points))









