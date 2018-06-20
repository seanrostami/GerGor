from GERGORCONFIG import ANIMNUMFRAMES


class GerGorAnimation():

	"""GerGorAnimation is responsible for producing the sequence of frames in an animation starting with a given "initial" position and ending with a given "terminal" position for a set of discs, and these positions are supplied to the constructor. Thereafter, the method .next_frame produces input suitable for GerGorPaintable.__init__ that, if painted, will depict the next frame in the animation. The boolean interpretation .__bool__ (or .__nonzero__ in v2) indicates whether the .next_frame method should be called at least one more time. If False, the frame most recently returned by .next_frame is the last frame available from GerGorAnimation and is exactly one frame prior to the terminal state (and therefore the terminal state itself should be painted separately immediately afterwards)."""

	def __init__( self, initialstate, terminalstate ):
		"""This constructor accepts two iterables of dictionaries (the same as those produced by GerGorComm.receive and GerGorMatrix.create_state) that are understood to describe 'before' and 'after' states of a set of discs (note: only single-use iterables are needed). Each dictionary must have the following form: { "center:(floating-point), "radius":(floating-point), "adrenaline":(boolean), "status":(string), ... }. Each iterable is traversed in parallel and the differences in any numerical quantities are divided into GERGORCONFIG.ANIMNUMFRAMES increments, which are later used by method .next_frame to interpolate between the 'before' and 'after' states. Non-numerical quantities are inherited either from the 'before' state or the 'after' state, as appropriate."""
		self.Initials = list( initialstate ) # store an internal copy (copies if already list, constructs list if non-list)
		self.Adrens = []
		self.cDeltas = []
		self.rDeltas = []
		for ( idd, tdd ) in zip( self.Initials, terminalstate ):
			self.Adrens.append( tdd["adrenaline"] ) # rules say adrenaline only allowed when one disc remains, so to call this a "list" is an exaggeration
			self.cDeltas.append( ( tdd["center"] - idd["center"] ) / ANIMNUMFRAMES ) # ("true" division since floating-point numerator)
			self.rDeltas.append( ( tdd["radius"] - idd["radius"] ) / ANIMNUMFRAMES ) # ("true" division since floating-point numerator)
		self.CurFrame = 0
# It is important that Adrenaline data is read from terminalstate, despite the fact that reading from initialstate (directly in .next_frame) would be cleaner. 
# When animating the opponent's previous move, the initial state is known from the current player's previous move and the terminal state is sent by the opponent to us. 
# However, Adrenaline was "disbursed" at the beginning of the opponent's turn and is therefore absent from the initial state and present in the terminal state.
# Similarly, if opponent had Adrenaline in the move before the previous move then we do NOT want to depict it in the Replay, but it will be present/absent in the initial/terminal state.
# Since current player's Adrenaline is held throughout the turn, the convention also yields correct results for animating the current player's move.

	def __bool__( self ): # boolean context does not trigger this in v2!
		"""BOOLEAN INTERPRETATION of GerGorAnimation: True if method .next_frame should be called again, False otherwise"""
		return self.CurFrame < ANIMNUMFRAMES

	def __nonzero__( self ): # analogue of __bool__ in v2
		"""BOOLEAN INTERPRETATION of GerGorAnimation: True if method .next_frame should be called again, False otherwise"""
		return self.__bool__()

	def next_frame( self ):
		"""This method, .next_frame, returns a list of dictionaries of the same form as those provided to the constructor __init__. Calling .next_frame the first time will produce the first frame in the animation. It is important to always check .__bool__ before calling .next_frame. Note that the value associated to the "status" key always comes from self.Initials."""
		frame = [ { "center":i["center"]+(self.CurFrame*cd), "radius":i["radius"]+(self.CurFrame*rd), "adrenaline":a, "status":i["status"] } for ( i, cd, rd, a ) in zip( self.Initials, self.cDeltas, self.rDeltas, self.Adrens ) ]
		self.CurFrame += 1
		return frame

