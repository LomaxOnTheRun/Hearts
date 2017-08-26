import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

from PIL import Image


WINDOW = Gdk.get_default_root_window()


def get_pixel_array_bytes(x, y, width, height):
	"""Gets the bytes from the pixel array selected"""
	pixbuf = Gdk.pixbuf_get_from_window(WINDOW, x, y, width, height)
	return pixbuf.get_pixels()

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


