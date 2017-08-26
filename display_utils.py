import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

from PIL import Image
#from fuzzywuzzy import fuzz


# NOTES ABOUT THIS CODE:
# - It works for Ubuntu 16.04 Hearts
# - The window must be at the default size
# - The window must be placed in the top right corner of the screen
# - Ubunutu's side bar must be hidden
# - The background colour must be changed to pure green (0, 255, 0)
#
# - I've taken out fuzzywuzzy matching to stop the warning coming up
#   I think it should work like this anyway, but if it can't recognise
#   cards any more, put it back in


WINDOW = Gdk.get_default_root_window()
PLAYER_HAND_X0 = 255
PLAYER_HAND_Y0 = 477


def get_pixel_array_bytes(x, y, width, height):
	"""Gets the bytes from the pixel array selected"""
	pixbuf = Gdk.pixbuf_get_from_window(WINDOW, x, y, width, height)
	return pixbuf.get_pixels()

def get_pixel(x, y):
	"""Gets a single pixel from screen"""
	return get_pixel_array_bytes(x, y, 1, 1)

def show_window(x, y, width, height):
	"""Returns list of rows of pixel hexs in window"""
	pixel_array_bytes = get_pixel_array_bytes(x, y, width, height)
	pixels_hex = pixel_array_bytes.hex()
	# Calculate num. of alpha pixels
	total_overhang = len(pixels_hex) - (width * height * 6)
	row_overhang = int(total_overhang / (height - 1))
	# Break into rows
	pixels = [pixels_hex[i*(6*width+row_overhang):(i+1)*(6*width+row_overhang)] for i in range(height)]
	# Remove alpha channel
	pixels = [row[:6*width] for row in pixels]
	# Break rows into pixels
	pixels = [[row[i:i+6] for i in range(0, len(row), 6)] for row in pixels]
	# Break pixels into list of RGB values
	pixels = [[[pixel[i*2:i*2+2] for i in range(3)] for pixel in row] for row in pixels]
	# Turn hex to decimals
	pixels = [[[int(colour, 16) for colour in pixel] for pixel in row] for row in pixels]
	# Draw image
	background = (100, 0, 0, 255)
	im = Image.new('RGB', (len(pixels[0]), len(pixels)), background)
	im_pixels = im.load()
	for col_index, row in enumerate(pixels):
		for row_index, pixel in enumerate(row):
			im_pixels[row_index, col_index] = tuple(pixel)
	im.show()

def get_num_cards_in_hand():
	"""Checks how many cards in player's hand"""
	pixel_array_bytes = get_pixel_array_bytes(255, 500, 240, 1)
	pixels = [pixel_array_bytes[i*3:(i+1)*3] for i in range(240)]
	green_pixels = pixels.count(b'\x00\xff\x00')
	cards_gone = int(green_pixels / 15)
	return 13 - cards_gone

def get_suit(pixel_bytes):
	"""Gets suit of card"""
	for suit in SUITS:
		if pixel_bytes == SUITS[suit]:
			return suit

def get_best_key(pixel_array):
	"""Return best guess at value of card"""
	best_key = ''
	max_ratio = 0
	for key in CARD_VALUES:
		value = CARD_VALUES[key]
		#ratio = fuzz.ratio(pixel_array, value)
		#if ratio > max_ratio:
		if pixel_array == value:
			max_ratio = ratio
			best_key = key
	return best_key

def get_card_value(x, y, show_pixel_array):
	"""Return value of card"""
	# This keeps getting confsed between 3 and 7, so use slices instead
	#pixel_array = get_pixel_array_bytes(x, y, 7, 11)
	# Use rows 2, 5, 9
	pixel_composite_array = ''
	for i in [1, 5, 9]:
		pixel_array = get_pixel_array_bytes(x, y+1, 7, 1)
		pixel_composite_array += pixel_array.hex()
	value = get_best_key(pixel_composite_array)
	if show_pixel_array:
		print(pixel_composite_array)
	return value[1:]

def get_cards(show_pixel_array=False):
	"""Get an array of the cards in player's hand"""
	num_cards = get_num_cards_in_hand()
	hand_start_x = PLAYER_HAND_X0 + int((13-num_cards)*15/2)
	suit_start_y = PLAYER_HAND_Y0 + 14
	value_start_y = PLAYER_HAND_Y0 + 3
	cards = []
	for i in range(num_cards):
		# First, get the suit
		x = hand_start_x + (i*15) + 5
		y = suit_start_y + 5
		pixel = get_pixel(x, y)
		suit = get_suit(pixel)
		# Then, get the card value
		x = hand_start_x + 3 + (i*15)
		y = value_start_y
		value = get_card_value(x, y, show_pixel_array)
		# Show final result
		cards.append(suit + value)
	return cards



# These are combines lines of 7 pixels
# for rows 2, 5, and 9 (0 is Y0+3)
CARD_VALUES = {
	# BLACKS
	'b2': '8d8d8d323232838383a6a6a69090903737378383838d8d8d323232838383a6a6a69090903737378383838d8d8d323232838383a6a6a6909090373737838383',
	'b3': '1c1c1c797979aaaaaaa3a3a35151511f1f1fc4c4c41c1c1c797979aaaaaaa3a3a35151511f1f1fc4c4c41c1c1c797979aaaaaaa3a3a35151511f1f1fc4c4c4',
	'b4': 'ffffffffffffffffff9999990c0c0c2d2d2de3e3e3ffffffffffffffffff9999990c0c0c2d2d2de3e3e3ffffffffffffffffff9999990c0c0c2d2d2de3e3e3',
	'b5': '6c6c6c494949aaaaaaaaaaaaaaaaaaaaaaaae2e2e26c6c6c494949aaaaaaaaaaaaaaaaaaaaaaaae2e2e26c6c6c494949aaaaaaaaaaaaaaaaaaaaaaaae2e2e2',
	'b6': 'c2c2c2313131797979a4a4a46a6a6a363636dadadac2c2c2313131797979a4a4a46a6a6a363636dadadac2c2c2313131797979a4a4a46a6a6a363636dadada',
	'b7': '1c1c1c797979aaaaaaaaaaaa9393932a2a2a6363631c1c1c797979aaaaaaaaaaaa9393932a2a2a6363631c1c1c797979aaaaaaaaaaaa9393932a2a2a636363',
	'b8': 'cecece323232a1a1a1eeeeee999999313131d9d9d9cecece323232a1a1a1eeeeee999999313131d9d9d9cecece323232a1a1a1eeeeee999999313131d9d9d9',
	'b9': 'e6e6e66060603a3a3a575757383838666666ececece6e6e66060603a3a3a575757383838666666ececece6e6e66060603a3a3a575757383838666666ececec',
	'b10': '242424b6b6b68787873b3b3b9a9a9a525252595959242424b6b6b68787873b3b3b9a9a9a525252595959242424b6b6b68787873b3b3b9a9a9a525252595959',
	'bJ': 'ffffffffffffffffffd5d5d57c7c7c535353adadadffffffffffffffffffd5d5d57c7c7c535353adadadffffffffffffffffffd5d5d57c7c7c535353adadad',
	'bQ': 'ececec5d5d5d585858a0a0a0525252666666f1f1f1ececec5d5d5d585858a0a0a0525252666666f1f1f1ececec5d5d5d585858a0a0a0525252666666f1f1f1',
	'bK': '919191252525929292e2e2e2494949373737a5a5a5919191252525929292e2e2e2494949373737a5a5a5919191252525929292e2e2e2494949373737a5a5a5',
	'bA': 'ffffffffffff888888121212929292ffffffffffffffffffffffff888888121212929292ffffffffffffffffffffffff888888121212929292ffffffffffff',
	# REDS
	'r2': 'f18d8de53232ef8383f4a6a6f19090e53737ef8383f18d8de53232ef8383f4a6a6f19090e53737ef8383f18d8de53232ef8383f4a6a6f19090e53737ef8383',
	'r3': 'e21c1cee7979f4aaaaf3a3a3e95151e21f1ff7c4c4e21c1cee7979f4aaaaf3a3a3e95151e21f1ff7c4c4e21c1cee7979f4aaaaf3a3a3e95151e21f1ff7c4c4',
	'r4': 'fffffffffffffffffff29999e00c0ce42d2dfbe3e3fffffffffffffffffff29999e00c0ce42d2dfbe3e3fffffffffffffffffff29999e00c0ce42d2dfbe3e3',
	'r5': 'ec6c6ce84949f4aaaaf4aaaaf4aaaaf4aaaafbe2e2ec6c6ce84949f4aaaaf4aaaaf4aaaaf4aaaafbe2e2ec6c6ce84949f4aaaaf4aaaaf4aaaaf4aaaafbe2e2',
	'r6': 'f7c2c2e53131ee7979f3a4a4ec6a6ae53636fadadaf7c2c2e53131ee7979f3a4a4ec6a6ae53636fadadaf7c2c2e53131ee7979f3a4a4ec6a6ae53636fadada',
	'r7': 'e21c1cee7979f4aaaaf4aaaaf19393e42a2aeb6363e21c1cee7979f4aaaaf4aaaaf19393e42a2aeb6363e21c1cee7979f4aaaaf4aaaaf19393e42a2aeb6363',
	'r8': 'f8cecee53232f3a1a1fceeeef29999e53131fad9d9f8cecee53232f3a1a1fceeeef29999e53131fad9d9f8cecee53232f3a1a1fceeeef29999e53131fad9d9',
	'r9': 'fce6e6eb6060e63a3aea5757e63838eb6666fcececfce6e6eb6060e63a3aea5757e63838eb6666fcececfce6e6eb6060e63a3aea5757e63838eb6666fcecec',
	'r10': 'e32424f5b6b6f08787e63b3bf29a9ae95252ea5959e32424f5b6b6f08787e63b3bf29a9ae95252ea5959e32424f5b6b6f08787e63b3bf29a9ae95252ea5959',
	'rJ': 'fffffffffffffffffff9d5d5ee7c7ce95353f4adadfffffffffffffffffff9d5d5ee7c7ce95353f4adadfffffffffffffffffff9d5d5ee7c7ce95353f4adad',
	'rQ': 'fcececea5d5dea5858f3a0a0e95252eb6666fdf1f1fcececea5d5dea5858f3a0a0e95252eb6666fdf1f1fcececea5d5dea5858f3a0a0e95252eb6666fdf1f1',
	'rK': 'f19191e32525f19292fbe2e2e84949e63737f3a5a5f19191e32525f19292fbe2e2e84949e63737f3a5a5f19191e32525f19292fbe2e2e84949e63737f3a5a5',
	'rA': 'fffffffffffff08888e11212f19292fffffffffffffffffffffffff08888e11212f19292fffffffffffffffffffffffff08888e11212f19292ffffffffffff',
}

SUITS = {'C': b'\x00\x00\x00',
		 'D': b'\xdf\x00\x00',
		 'S': b'\x02\x02\x02',
		 'H': b'\xdf\x04\x04'}


