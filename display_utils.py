import gi
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk

from PIL import Image


def show_window(x, y, width, height):
	"""Returns list of rows of pixel hexs in window"""
	window = Gdk.get_default_root_window()
	pixbuf = Gdk.pixbuf_get_from_window(window, x, y, width, height)
	pixels_byte = pixbuf.get_pixels()
	pixels_hex = pixels_byte.hex()
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

