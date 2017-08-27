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

