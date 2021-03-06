from random import shuffle, randint, choice, random
from itertools import combinations
from sys import stdout

import matplotlib.pyplot as plt


SUITS_FULL = ['C', 'D', 'S', 'H']
VALUES_FULL = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

SUITS = ['H', 'S']
#VALUES = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
#SUITS = ['S']
#VALUES = ['7', '8', '9', '10', 'J', 'Q', 'K', 'A']
VALUES = ['9', '10', 'J', 'Q', 'K', 'A']
# VALUES = ['J', 'Q', 'K', 'A']
# VALUES = VALUES_FULL


class Game:
	"""This keeps all the game metadata"""
	def __init__(self, num_players=4, num_hands=1000, learning_rate=0.1, discount_factor=0.9, greediness=0.9):
		# User selected info
		self.num_players = num_players
		self.num_hands = num_hands
		self.deck = create_deck()
		self.hands_list = None
		# Learning hyperparameters
		self.learning_rate = learning_rate
		self.discount_factor = discount_factor
		self.greediness = greediness  # The greedier, the more likely to pick the best move
		# Cumulative record
		self.hand_num = 0
		self.cumulative_scores = [0] * num_players
		self.hands_won = [0] * num_players
		self.points_won = [0] * num_players
		self.percentage_points = []
		# Switches that get reset every hand
		self.first_trick = True
		self.hearts_broken = False
		# Debug options
		self.show_play = False
		self.show_Q_values = False
		self.show_scores = False
		self.show_final_Q = False
		self.show_running_scores = False
		self.show_final_scores = True
		self.show_points_won_per_hand = False
		# Percentage tracker
		self.current_percentage = 0
		self.new_percentage = False
		# Testing stuff
		if self.num_players == 2:
			self.unique_hand_codes = self.get_unique_hand_codes_2()
		elif self.num_players == 3:
			# self.unique_hand_codes = self.get_unique_hand_codes_3()
			pass
		else:
			# DO NOT USE THIS, EVEN WITH 4 CARDS EACH, IT'S A MILLION COMBINATIONS
			# self.unique_hand_codes = self.get_unique_hand_codes_4()
			pass
		self.run_assessment_tests = False

	def set_hands(self, hands_list):
		"""
		Takes a list of list of card codes for values

		e.g. [['H2', 'H3'],  # Player 0
			  ['H4', 'H5']]  # Player 1
		"""
		self.hands_list = hands_list
		self.num_players = len(hands_list)
		self.deck = []

		players = [Player(i) for i in range(len(hands_list))]
		for index, hand in enumerate(hands_list):
			player = players[index]
			player.hand = []
			for card_str in hand:
				card = Card(card_str[0], card_str[1:])
				player.hand.append(card)
				self.deck.append(card)
		set_first_lead(players, self)
		if self.num_players == 2:
			self.unique_hand_codes = self.get_unique_hand_codes_2()
		elif self.num_players == 3:
			# self.unique_hand_codes = self.get_unique_hand_codes_3()
			pass
		else:
			# DO NOT USE THIS, EVEN WITH 4 CARDS EACH, IT'S A MILLION COMBINATIONS
			# self.unique_hand_codes = self.get_unique_hand_codes_4()
			pass
		return players

	def update_points_won(self, points):
		self.points_won = [sum(x) for x in zip(self.points_won, points)]

	def get_deck_codes(self):
		return [card.code for card in self.deck]

	def get_unique_hand_codes_2(self):
		"""Split a set of cards into tuples of hands - THIS ONLY WORKS FOR 2 PLAYERS"""
		deck_codes = self.get_deck_codes()
		num_cards_in_hand = int(len(deck_codes) / self.num_players)
		unique_hands = [hand for hand in combinations(deck_codes, num_cards_in_hand)]
		unique_hands_2 = [hand for hand in unique_hands]
		unique_hands_2.reverse()
		return list(zip(unique_hands, unique_hands_2))

	# def get_unique_hand_codes_3(self):
	# 	deck_codes = self.get_deck_codes()
	# 	num_cards_in_hand = int(len(deck_codes) / self.num_players)
	# 	unique_hands = []
	# 	unique_player0_hands = list(combinations(deck_codes, num_cards_in_hand))
	# 	for player0_hand in unique_player0_hands:
	# 		deck_codes = self.get_deck_codes()
	# 		for card in player0_hand:
	# 			deck_codes.remove(card)
	# 		unique_player1_hands = list(combinations(deck_codes, num_cards_in_hand))
	# 		for player1_hand in unique_player1_hands:
	# 			reduced_deck = [card for card in deck_codes]
	# 			for card in player1_hand:
	# 				reduced_deck.remove(card)
	# 			player2_hand = tuple(reduced_deck)
	# 			unique_hands.append((player0_hand, player1_hand, player2_hand))
	# 	return unique_hands

	# def get_unique_hand_codes_4(self):
	# 	"""DO NOT USE THIS, EVEN 4 CARDS PER PERSON HAS A MILLION COMBINATIONS"""
	# 	deck_codes = self.get_deck_codes()
	# 	num_cards_in_hand = int(len(deck_codes) / self.num_players)
	# 	unique_hands = []
	# 	unique_player0_hands = list(combinations(deck_codes, num_cards_in_hand))
	# 	for player0_hand in unique_player0_hands:
	# 		deck_codes = self.get_deck_codes()
	# 		for card in player0_hand:
	# 			deck_codes.remove(card)
	# 		unique_player1_hands = list(combinations(deck_codes, num_cards_in_hand))
	# 		for player1_hand in unique_player1_hands:
	# 			reduced_deck = [card for card in deck_codes]
	# 			for card in player1_hand:
	# 				reduced_deck.remove(card)
	# 			unique_player2_hands = list(combinations(reduced_deck, num_cards_in_hand))
	# 			for player2_hand in unique_player2_hands:
	# 				final_cards = [card for card in reduced_deck]
	# 				for card in player2_hand:
	# 					final_cards.remove(card)
	# 				player3_hand = tuple(final_cards)
	# 			unique_hands.append((player0_hand, player1_hand, player2_hand, player3_hand))
	# 	return unique_hands


class Card:
	def __init__(self, suit, value_str):
		self.suit = suit
		self.value = self.get_value(value_str)
		self.code = suit + value_str
		self.points = self.get_points()
		self.sort_value = 100 * SUITS_FULL.index(suit) + VALUES_FULL.index(value_str)

	def __repr__(self):
		return self.code

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

	def get_card_from_hand(self, card_code):
		for card in self.hand:
			if card.code == card_code:
				return card
		return None

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
				return [get_lowest_card(game)]
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
			print(trick)
			print(self.get_hand_codes())
		card_to_play = choice(legal_moves)
		return card_to_play

	def get_lowest_playable_card(self, trick, game):
		legal_moves = self.get_legal_moves(trick, game)
		lowest_card = None
		for card_code in legal_moves:
			card = self.get_card_from_hand(card_code)
			if not lowest_card or card.sort_value < lowest_card.sort_value:
				lowest_card = card
		return lowest_card.code

	def sort_hand(self):
		sort_values = [card.sort_value for card in self.hand]
		while sort_values:
			min_index = sort_values.index(min(sort_values))
			self.hand.append(self.hand.pop(min_index))
			del sort_values[min_index]


def set_up_game(game):
	players = shuffle_and_deal_cards(game)
	if game.hands_list:
		players = game.set_hands(game.hands_list)
	set_first_lead(players, game)
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


def shuffle_and_deal_cards(game):
	"""Shuffle and deal cards"""
	players = [Player(i) for i in range(game.num_players)]
	deck = [card for card in game.deck]
	shuffle(deck)
	if len(deck) % game.num_players != 0:
		raise Exception('Deck size not divisable by number of players: {} / {}'.format(len(deck), game.num_players))
	hand_size = int((len(SUITS) * len(VALUES)) / game.num_players)
	for player in players:
		player.hand = deck[:hand_size]
		del deck[:hand_size]
		player.sort_hand()
	return players


def set_first_lead(players, game):
	"""Find first player to start game with C2"""
	for player in players:
		lowest_card = get_lowest_card(game)
		if lowest_card in player.get_hand_codes():
			player.lead = True
			break


def create_deck():
	"""Creates a deck using the SUITS and VALUES"""
	return [Card(suit, value_str) for suit in SUITS for value_str in VALUES]


def get_lowest_card(game):
	"""Returns the code for the lowest card in the deck"""
	# Split deck into suits
	suit_split_cards = [[] for suit in SUITS_FULL]
	for card in game.deck:
		for index, suit in enumerate(SUITS_FULL):
			if card.suit == suit:
				suit_split_cards[index].append(card)

	for suit_cards in suit_split_cards:
		if suit_cards:
			min_card = suit_cards[0]
			for card in suit_cards:
				if card.value < min_card.value:
					min_card = card
			return min_card.code
	return None


def put_players_in_turn_order(players):
	"""Put players in correct turn order"""
	while not players[0].lead:
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
		#card_to_play = player.get_random_legal_card_to_play(trick, game)
		# Always play lowest value card
		card_to_play = player.get_lowest_playable_card(trick, game)

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


def get_ordered_deck_codes(game):
	sorted_deck = sorted(game.deck, key=lambda x: x.sort_value)
	sorted_deck = [card.code for card in sorted_deck]
	return sorted_deck


###################
#   DEBUG UTILS   #
###################


def show_hands(players):
	for player in players:
		print('player{} - {}'.format(player.id_val, player.get_hand_codes()))


def get_percentage_points(points_list):
	total_points = sum(points_list)
	player_0_points = float(points_list[0])
	percentage_points = round(((player_0_points / total_points) * 100), 2)
	return percentage_points


def show_final_scores(game):
	print('\nCumulative scores:\t{}'.format(game.cumulative_scores))
	print('Hands won:\t\t{}'.format(game.hands_won))
	percentage_points = get_percentage_points(game.cumulative_scores)
	print('% of points gained:\t{}%'.format(percentage_points))


def show_best_score_for_hands(points_won_for_hand):
	print('\nBest score for every starting hand:\n')
	for hands, points in points_won_for_hand:
		print(hands, points)


def show_cummulative_scores(game, hand_num):
	# TODO: If we keep this in, add ability to set how often we show scores
	if game.show_scores and hand_num % 10000 == 0:
		print('\n#{} - {}'.format(hand_num, game.cumulative_scores))
		game.cumulative_scores = [0] * num_players


###############
#   LOGGING   #
###############


def do_pre_hand_logging(game, hand_num):
	# Hand counter
	game.new_percentage = False
	hand_percentage = int((hand_num * 100.0) / game.num_hands) + 1
	if hand_percentage > game.current_percentage:
		game.new_percentage = True
		stdout.write('{}Running games [{}%]'.format('\b'*20, hand_percentage))
		stdout.flush()

	# Show cumulative scores per X number of games
	show_cummulative_scores(game, hand_num)


def do_post_hand_logging(game, model, players, hand_num, test_model):
	# Update cummulative scores
	for i, player in enumerate(players):
		game.cumulative_scores[i] += player.points

	# Get winners for current game
	points = [player.points for player in players]
	game.update_points_won(points)
	min_points = min(points)
	winners = [index for index, point in enumerate(points) if point == min_points]
	for winner in winners:
		game.hands_won[winner] += 1

	if game.new_percentage:
		if game.show_running_scores:
			row_format = '{:>15}' * game.num_players
			print(row_format.format(*game.points_won))
			game.points_won = [0] * game.num_players
		if game.run_assessment_tests:
			percentage_points = test_model(game, model)
			game.percentage_points.append(percentage_points)
		hand_percentage = int((hand_num * 100.0) / game.num_hands) + 1
		game.current_percentage = hand_percentage


def do_post_game_logging(game, model, test_model):
	if game.show_final_Q:
		show_Q(model, game)

	if game.show_final_scores:
		show_final_scores(game)

	if game.run_assessment_tests:
		# Do final assessment and show total
		percentage_points = test_model(game, model)
		game.percentage_points.append(percentage_points)
		print('\n', game.percentage_points, '\n')

	if game.show_points_won_per_hand:
		show_best_score_for_hands(points_won_for_hand)


def show_percentage_points_graph(game):
	num_points = len(game.percentage_points)
	x_step = int(game.num_hands / (num_points - 1))
	x = range(0, game.num_hands+1, x_step)
	y = game.percentage_points
	plt.plot(x, y)
	plt.ylabel('% of points gained')
	plt.xlabel('Number of hands played')
	plt.title('% points earned by Player 0 ({} total players)\n'
			  'Deck: {}'.format(game.num_players, game.get_deck_codes()))
	plt.show()
