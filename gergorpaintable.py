from GERGORCONFIG import IMGMYCOLOR, IMGOPPCOLOR, IMGDISTINGUISHCOLOR, IMGMYADRENALINECOLOR, IMGOPPADRENALINECOLOR


class GerGorPaintable():

	"""GerGorPaintable is responsible for converting raw data describing the positions of the two players to a single list of dictionaries that conveniently expose the data that class GerGorImage needs to draw the game screen. At any time after construction, a GerGorImage's graphics buffer can be updated with the game state thus represented by passing it to the GerGorPaintable.paint method."""

	def __init__( self, homestate, awaystate ):
		"""This constructor accepts a two LISTs of dictionaries containing raw data describing the positions of the two players. Each dictionary must have the following form: { "center":(floating-point), "radius":(floating-point), "adrenaline":(boolean), ... }. The dictionary constructed from these, internal to GerGorPaintable, is suitable for input to the GerGorImage.draw method. Each parameter is traversed twice, so each must be a LIST, not merely a generator."""
		self.PaintQueue = []
		adrenchecker = ( lambda dd : ( True if dd["adrenaline"] else False ) )
		self.Adrenalized = any( map( adrenchecker, awaystate ) ) # draw centers of our discs if the opponent has adrenaline
		for hdd in homestate:
			self.PaintQueue.append( { "center":hdd["center"], "radius":hdd["radius"], "fill":(IMGMYADRENALINECOLOR if hdd["adrenaline"] else IMGMYCOLOR), "centered":self.Adrenalized } )
		self.Adrenalized = any( map( adrenchecker, homestate ) ) # draw centers of a opponent's discs if we have adrenaline
		for add in awaystate:
			self.PaintQueue.append( { "center":add["center"], "radius":add["radius"], "fill":(IMGOPPADRENALINECOLOR if add["adrenaline"] else IMGOPPCOLOR), "centered":self.Adrenalized } )

	def distinguish( self, i, on ):
		"""This method, .distinguish, merely "highlights" or "unhighlights" one particular disc. Warning: At present, this method is used only by the SHOW button and therefore assumes that the disc belongs to the current player. This means that the non-highlighted color is fixed."""
		(self.PaintQueue[i])["fill"] = ( IMGDISTINGUISHCOLOR if on else ( IMGMYADRENALINECOLOR if self.Adrenalized else IMGMYCOLOR ) )

	def paint( self, ggi, gtkimage ):
		"""This method, .paint, accepts a GerGorImage object ggi and invokes its methods to draw self's game state to ggi's graphics buffer, and then paints that buffer on the given GtkImage widget."""
		ggi.reset()
		ggi.draw( self.PaintQueue )
		ggi.flush( gtkimage )

