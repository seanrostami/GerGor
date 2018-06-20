from PIL import Image, ImageColor, ImageDraw

from GERGORCONFIG import IMGHEIGHT, IMGWIDTH, IMGMAGNIFY, IMGPLANECOLOR, IMGAXISCOLOR, IMGAXISTHICKNESS, IMGOUTLINECOLOR, IMGCENTERDOTRADIUS

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib


class GerGorImage():

	"""GerGorImage performs all construction, via PIL, of genuine image data and performs all display, via GTK+, of said data. In this prototype, GerGorImage uses the PIL library to create in RAM an image that depicts the game's numerical/logical data, and GTK+ then loads the image into the appropriate window so that it is visible to the player. The typical pattern of usage is:
	1) possess an iterable I of certain dictionaries (class GerGorPaintable constructs such dictionaries), 
	2) call .reset() to revert the image data to its "neutral" state, 
	3) call .draw(I) to paint each disc in I to the image data, 
	4) call .flush(W) to write the finished image to the GtkImage widget W.
GerGorImage is ignorant of the gameplay details. For example, GerGorImage does not know which disc belongs to which player, and merely draws the color specified by each dictionary. Conversely, GerGorImage handles some visibility details that need not concern the rest of the program. For example, although all relative sizes (e.g. Height-to-Width ratio) are specified outside of GerGorImage, the absolute size of the whole image is controlled within GerGorImage via the constant GERGORCONFIG.IMGMAGNIFY. Note: GdkPixbuf and the module PIL are not used in any other part of the program (except for GERGORCONFIG.py, which uses PIL merely to convert from human-readable color names to RGB values)."""

	def __init__( self, w = IMGWIDTH, h = IMGHEIGHT ):
		self.Img = Image.new( "RGB", ( int(round(IMGMAGNIFY*w)), int(round(IMGMAGNIFY*h)) ), IMGPLANECOLOR ) # not yet exploiting the possibility of "alpha"
		self.Drawer = ImageDraw.Draw( self.Img, "RGB" )
		self.glibbytesA = None
		self.glibbytesB = None
		self.ABalternator = True
		self.gdkpixbuf = None

	def __del__( self ):
		self.Img.close()

	def get_origin( self ):
		"""[PRIVATE] This method, .get_origin, merely returns the screen coordinates of the point that players consider to be the origin: the intersection of the two axes."""
		return self.Img.width // 2, self.Img.height // 2 # truncate to integer

	def reset( self ):
		"""This method, .reset, merely writes axes on a blank background to self's PIL.Image graphics object. Usually (always?) this is done after the data of one or more discs changes and therefore must be redrawn. The data is not actually displayed -- this is done when desired by .flush method."""
		self.Drawer.rectangle( xy = [ ( 0, 0 ), ( self.Img.width, self.Img.height ) ], fill = IMGPLANECOLOR )
		ox, oy = self.get_origin()
		self.Drawer.line( [ ( 0, oy ), ( self.Img.width, oy ) ], fill = IMGAXISCOLOR, width = IMGAXISTHICKNESS )
		self.Drawer.line( [ ( ox, 0 ), ( ox, self.Img.height ) ], fill = IMGAXISCOLOR, width = IMGAXISTHICKNESS )

	def draw_disc( self, c, r, f, o = IMGOUTLINECOLOR ):
		"""[PRIVATE] This method, .draw_disc, draws a disc with center c, radius r, fill color f, and (optional) outline color o to self's PIL.Image graphics object. Since GerGor uses only discs whose centers are on the horizontal axis, parameter c is a single number. Coordinate c is should be interpreted relative to the intersection of the two axes, i.e. in the mathematical world where the origin is actually (0,0). Conversion of c to true coordinates, i.e. in the computer world where (0,0) is the bottom-left corner, is done here. The data is not actually displayed -- this is done when desired by .flush method."""
		ox, oy = self.get_origin()
		self.Drawer.ellipse( xy = [ ( ox + int(round((IMGMAGNIFY*(c-r)))), oy - int(round((IMGMAGNIFY*r))) ), ( ox + int(round((IMGMAGNIFY*(c+r)))), oy + int(round((IMGMAGNIFY*r))) ) ], fill = f, outline = o )

	def draw( self, dds ):
		"""This method, .draw, accepts an iterable (note: only single-use iterables are needed) of certain dictionaries and writes them all to self's PIL.Image graphics object in an intelligent way. Each dictionary must have the following form: { "center":(floating-point), "radius":(floating-point), "fill":(RGB-triple as in PIL), "centered":(boolean), ... }. Currently, 'intelligent' means that the discs are drawn in decreasing order of radius, so that no disc is completely blocked by another disc. This seems to produce a good overall experience, but may be improved somehow in the future."""
		for dd in sorted( dds, key = ( lambda d : d["radius"] ), reverse = True ): # draw larger discs earlier
			self.draw_disc( dd["center"], dd["radius"], dd["fill"] )
			if dd["centered"]: # possibly draw center (relevant for 'Adrenaline')
				self.draw_disc( dd["center"], IMGCENTERDOTRADIUS, IMGOUTLINECOLOR ) # a thick dot

	def flush( self, gtkimage ):
		"""This method, .flush, tells the given GtkImage widget to load this GerGorImage's current graphics buffer. This GerGorImage's current graphics buffer will be displayed immediately on the player's screen."""
		if self.ABalternator:
			self.glibbytesA = GLib.Bytes.new( self.Img.tobytes() )
		else:
			self.glibbytesB = GLib.Bytes.new( self.Img.tobytes() )
		self.gdkpixbuf = GdkPixbuf.Pixbuf.new_from_bytes( ( self.glibbytesA if self.ABalternator else self.glibbytesB ), GdkPixbuf.Colorspace.RGB, False, 8, self.Img.width, self.Img.height, len(self.Img.getbands())*self.Img.width )
		self.ABalternator = not self.ABalternator # toggle value
		gtkimage.set_from_pixbuf( self.gdkpixbuf.copy() )
# I learned that PIL.Image could be painlessly converted to GdkPixbuf from the module "pixbuf2pillow" at https://gist.github.com/mozbugbox/10cd35b2872628246140/. 
# However, use of pixbuf2pillow's function image2pixbuf, or any inline equivalent of it, in method GerGorImage.flush produces a MASSIVE memory leak. 
# This seems to be a known issue, cf. https://gitlab.gnome.org/GNOME/pygobject/issues/127 . 
# My first attempt to resolve the memory leak was to use GdkPixbuf.Pixbuf.new_from_data, because it does not duplicate its argument. 
# However, there were crashes because GdkPixbuf.Pixbuf.new_from_data has its own problems... cf. https://gitlab.gnome.org/GNOME/pygobject/issues/225 . 
# Ultimately, simply passing pixbuf.copy() instead of pixbuf to GtkImage.set_from_pixbuf seems to allow garbage-collection to function properly and eliminates the memory leak. 
# I warmly thank Christopher Reiter of https://gitlab.gnome.org/GNOME/pygobject/ for helping me to understand .new_from_data vs. .new_from_bytes and for suggesting the workaround. 

