import os

import random # NOT SEEDED HERE!

from GERGORCONFIG import COMMRANDMIN, COMMPREFIX, COMMSUFFIX, COMMSTUB


class GerGorComm():

	"""GerGorComm is responsible for all communication with the opponent, which is non-trivial because each player operates an independent instance of the game. At the end of a player's turn, the current state of the game is fully known only to that player, and therefore must be transmitted in some way to the opponent. In this prototype, this is accomplished as follows: each instance of the game creates its own temporary file at launch (.__init__), receives data by reading its own file (.receive), and sends data by writing to the opponent's file (.send). While waiting for the opponent to finish a turn, an instance of the game uses a GTK+ timeout (cf. standby_timeout in GERGORCALLBACKS.py) to monitor (.__bool__ or .__nonzero__) the receiving file for data. To implement 'Replay' functionality, it is also necessary to access the *previous* state of the opponent's discs, and this is also managed by GerGorComm (.get_previous_data).
	Notes: 
	1) No other file uses any of the built-in open/.write/.readline/close file functions. 
	2) The constructor __init__ uses random.randrange, and it is the responsibility of the user of GerGorComm to seed the generator.
	3) The decision to use an independent instance of the game for each player was made so that remote play might later be added with minimal changes to the basic design."""

	def __init__( self ):
		self.ReadID = random.randrange( COMMRANDMIN, 10*COMMRANDMIN ) # random integer, randomizes communication file's name (next)
		self.ReadFile = COMMPREFIX + str( self.ReadID ) + os.extsep + COMMSUFFIX
		self.ReadLoc = os.path.join( os.getcwd(), self.ReadFile )
		self.WriteLoc = "" # need attribute to exist because method .send will be called on Quit, possibly before connected to opponent
		self.erase() # create empty file -- opponent will transmit data to us via this file
		self.LastKnownOpponentData = []
		self.NewestOpponentData = []

	def __del__( self ):
		if os.path.isfile( self.ReadLoc ):
			os.remove( self.ReadLoc ) # is it possible that might try to remove the file while the opponent is writing to it?

	def __bool__( self ): # boolean context does not trigger this in v2!
		"""BOOLEAN INTERPRETATION of GerGorComm: True if the receiving file contains data, False otherwise."""
		return ( os.path.getsize( self.ReadLoc ) > 0 ) # check if end-of-turn data is available from opponent

	def __nonzero__( self ): # analogue of __bool__ in v2
		"""BOOLEAN INTERPRETATION of GerGorComm: True if the receiving file contains data, False otherwise."""
		return self.__bool__()

	def get_ID( self ):
		return self.ReadID

	def get_read_location( self ):
		return self.ReadLoc

	def set_write_location( self, wloc ):
		"""This method, .set_write_location, attempts to check the correctness of the given opponent's location and then, if correct, records it. The opponent's randomly-generated ID is also extracted from the filename."""
		if ( len( wloc ) == 0 ) or ( wloc == self.ReadLoc ) or ( not os.path.isfile( wloc ) ): # reject bad locations: empty descriptor, self-referential, non-existent
			return False
		self.WriteLoc = wloc
		self.WriteID = int( wloc[ wloc.rfind( COMMPREFIX ) + len( COMMPREFIX ) : len( wloc ) - len( os.extsep + COMMSUFFIX ) ] )
		return True

	def is_first( self ):
		"""This method, .is_first, merely determines which player should play first. Each player has a randomly-generated integer ID (see .__init__), and the player with the higher ID plays first. The opponent's ID is deduced in the .set_write_location method."""
		assert self.ReadID != self.WriteID, "Both players were assigned the same randomly-generated ID?!"
		return self.ReadID > self.WriteID # player with the higher ID goes first

	def receive( self ):
		"""This method, .receive, reads (from a file in the working directory on the local disk) all data sent to us at the end of the opponent's turn into a list of dictionaries and returns a copy of that list. This data describes the state of all the opponent's discs and is used to synchronize the local state of the game with that of the opponent. The dictionaries so produced have the following form: { "center:(floating-point), "radius":(floating-point), "adrenaline":(boolean), "status":(string) }. To implement 'Replay' functionality, the most recently known such data is saved before overwriting with new data. Finally, the input file is erased and therefore can be properly monitored (by .__bool__) after we end our current turn for data from the opponent's subsequent turn. Although it might seem more natural to call .erase at the beginning of .send, it is wrong to do so: the opponent might Quit while we are playing our own turn, data indicating this would be immediately sent to our file, but that file would then be erased when we finally finished our turn, and we would then wait forever for a non-existent opponent to finish a turn. In a future, network-capable version of the game, data will instead be read from a socket."""
		self.LastKnownOpponentData = list( self.NewestOpponentData ) # for Replay, save previous state of opponent (.copy for Lists not in v2)
		rfile = open( self.ReadLoc, 'r' )
		rfile.readline() # discard the dummy header COMMSTUB
		self.NewestOpponentData[:] = [] # clear the list (.clear for Lists not in v2)
		c = rfile.readline() # read the first "center" value, if exists
		while bool( c ): # if there is a "center", there will always be a complete record
			r = rfile.readline()
			a = rfile.readline()
			s = rfile.readline()
			self.NewestOpponentData.append( { "center":float(c), "radius":float(r), "adrenaline":int(a), "status":s } )
			c = rfile.readline() # read the next "center" value, if exists
		rfile.close()
		self.erase() # DO NOT MOVE TO .send (see docstring)
		return list( self.NewestOpponentData ) # protect this mutable list, return a copy (.copy for Lists not in v2)

	def erase( self ):
		"""[PRIVATE] This method, .erase, merely erases the file from which we receive end-of-turn data from the opponent. It is by the presence of data in this file (which is tested by the .__bool__ method) that we know the opponent's turn is finished, so this file must be empty prior to the start of the opponent's turn. Method .erase is used by method .receive to accomplish this."""
		open( self.ReadLoc, 'w' ).close()

	def get_newest_data( self ):
		return list( self.NewestOpponentData ) # protect this mutable list, return a copy (.copy for Lists not in v2)

	def get_newest_data_mutable( self ):
		"""This method, .get_newest_data_mutable, deliberately returns the internal copy of the opponent's data, presumably for modification. There are cases (most importantly GerGorMatrix.implement_gains) in which this data must be updated."""
		return self.NewestOpponentData # deliberately not protected

	def get_previous_data( self ):
		"""This method, .get_previous_data, is usually (always?) called when 'Replay' functionality is needed: a Replay is simply an animation interpolating from the data returned by .get_newest_data to the data returned by .get_previous_data."""
		return list( self.LastKnownOpponentData ) # protect this mutable list, return a copy (.copy for Lists not in v2)

	def send( self, homestate ):
		"""This method, .send, writes (to a file in the opponent's working directory somewhere on the local disk) an iterable of dictionaries containing all relevant information regarding our discs (note: only single-use iterables are needed). The dictionaries must have the following form: { "center:(floating-point), "radius":(floating-point), "adrenaline":(boolean), "status":(string), ... }. We signal to the opponent that we Quit or that we Lose (more precisely, we confirm that we Lose) by passing argument None. In a future, network-capable version of the game, data will instead be read from a socket."""
		if os.path.isfile( self.WriteLoc ): # don't create if it doesn't already exist, because maybe file was deleted by opponent on Quit...
			wfile = open( self.WriteLoc, 'w' ) # ... but if it does exist then overwrite
			wfile.write( COMMSTUB + os.linesep ) # write the dummy header
			if homestate is not None:
				for hdisc in homestate:
					wfile.write( str( hdisc["center"] ) + os.linesep + str( hdisc["radius"] ) + os.linesep + str( hdisc["adrenaline"] ) + os.linesep + hdisc["status"] + os.linesep )
			wfile.close()

