import random # NOT SEEDED HERE!

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from GERGORCONFIG import check_capture, is_current, isnt_evolved
from GERGORCONFIG import MATRIXDIM, MATRIXENTRYRANGE, MATRIXMINSIGNS, MATRIXRADIUSPOSRANGE, MATRIXRADIUSWEIGHT, MATRIXGROWTHFACTOR, MATRIXDECAYFACTOR
from GERGORCONFIG import MATRIXCAPTUREDPANGOFMT, MATRIXCENTRALENTRYPANGOFMT, MATRIXRADIALENTRYPANGOFMT


class GerGorMatrixEntry():

	def __init__( self ): # details may change later...
		self.Entry = MATRIXENTRYRANGE*random.random()

	def negate( self ):
		self.Entry *= -1

	def evolve( self, grow ): # details may change later...
		self.Entry *= ( MATRIXGROWTHFACTOR if grow else MATRIXDECAYFACTOR )

	def get_entry_exact( self ):
		return self.Entry

	def set_GtkWidget( self, widget ):
		"""This method, .set_GtkWidget, specifies the GtkWidget (usually a GtkButton containing a GtkLabel) that is used by the player to select this matrix entry. Each instance of GerGorMatrixEntry is responsible for activating, deactivating, and labeling its own GtkWidget. The commands to do such are delegated by whatever instance of GerGorMatrixRow contains this instance of GerGorMatrixEntry."""
		self.Widget = widget

	def get_GtkWidget( self ):
		return self.Widget

	def refresh_GtkWidget( self, isfocus ):
		"""This method, .refresh_GtkWidget, merely sets the text of this entry's GtkButton to a suitably rounded approximation of the entry's current value and includes some extra decoration (via Pango Markup) for convenience. The command to do such is delegated by whatever instance of GerGorMatrixRow contains this instance of GerGorMatrixEntry. Strictly speaking, the text is owned by a GtkLabel and the GtkLabel is the only child of the GtkButton (the latter being a GtkBin)."""
		self.Widget.get_child().set_markup( ( MATRIXCENTRALENTRYPANGOFMT if isfocus else MATRIXRADIALENTRYPANGOFMT ) % self.Entry )

	def enable_GtkWidget( self ):
		"""This method, .enable_GtkWidget, is inverse of the method disable_GtkWidget. The command to do such is delegated by whatever instance of GerGorMatrixRow contains this instance of GerGorMatrixEntry."""
		self.Widget.set_sensitive( True ) # .set_sensitive is a general GtkWidget method, independent of the particular widget

	def disable_GtkWidget( self ):
		"""This method, .disable_GtkWidget, deactivates the GtkWidget (probably a GtkButton), so it cannot be selected by the player. The command to do such is delegated by whatever instance of GerGorMatrixRow contains this instance of GerGorMatrixEntry."""
		self.Widget.set_sensitive( False ) # .set_sensitive is a general GtkWidget method, independent of the particular widget
	
	def capture( self ):
		self.disable_GtkWidget()
		self.Widget.get_child().set_markup( MATRIXCAPTUREDPANGOFMT )

class GerGorMatrixRow():

	def __init__( self, size, focus ): # details may change later...
		self.Entries = [ GerGorMatrixEntry() for _ in range( size ) ]
		numneg = random.randrange( MATRIXMINSIGNS, 1+MATRIXDIM-MATRIXMINSIGNS ) # how many to make negative
		tonegate = random.sample( self.Entries, numneg ) # which to make negative
		for e in tonegate:
			e.negate()
		self.CurFocus = self.PrevFocus = focus
		self.Captured = False
		self.Adrenalized = False

	def align( self, posdiag ):
		if posdiag == ( self.Entries[ self.CurFocus ].get_entry_exact() > 0 ):
			for e in self.Entries:
				e.negate() # if focus has "wrong" sign, flip all signs in that row

	def get_center( self ):
		return self.Entries[ self.CurFocus ].get_entry_exact()

	def get_radius( self ): # details may change later...
		return sum( [ ( MATRIXRADIUSWEIGHT**abs( i ) )*abs( self.Entries[ ( self.CurFocus + i ) % MATRIXDIM ].get_entry_exact() ) for i in range( -MATRIXRADIUSPOSRANGE, MATRIXRADIUSPOSRANGE+1 ) if i != 0 ] )

	def __bool__( self ): # boolean context does not trigger this in v2!
		"""BOOLEAN INTERPRETATION of GerGorMatrixRow: False if captured, True otherwise"""
		return not self.Captured

	def __nonzero__( self ): # equivalent of __bool__ in v2
		"""BOOLEAN INTERPRETATION of GerGorMatrixRow: False if captured, True otherwise"""
		return self.__bool__()

	def evolve( self, grow ): # details may change later...
		for i in filter( ( lambda i : i != self.CurFocus ), range( MATRIXDIM ) ):
			self.Entries[i].evolve( grow )

	def adrenalize( self, state ):
		self.Adrenalized = state

	def is_adrenalized( self ):
		return self.Adrenalized

	def capture( self ):
		self.Captured = True
		for e in self.Entries:
			e.capture()

	def get_current_focus( self ):
		return self.CurFocus

	def set_current_focus( self, j ):
		self.CurFocus = j

	def set_previous_focus_to_current( self ):
		self.PrevFocus = self.CurFocus

	def revert_focus( self ):
		self.CurFocus = self.PrevFocus

	def get_random_GerGorMatrixEntry( self, allowfocus = False ):
		return self.Entries[ random.choice( range( MATRIXDIM ) if allowfocus else list( filter( ( lambda i : i != self.CurFocus ), range( MATRIXDIM ) ) ) ) ]

	def set_GtkWidgets( self, widget, j, showbutton ):
		self.Entries[j].set_GtkWidget( widget )
		self.ShowButton = showbutton

	def refresh_GtkWidgets( self ):
		for ( i, e ) in enumerate( self.Entries ):
			e.refresh_GtkWidget( i == self.CurFocus )

	def enable_GtkWidgets( self ):
		for e in self.Entries:
			e.enable_GtkWidget()
		self.ShowButton.set_sensitive( True ) # .set_sensitive is a general GtkWidget method, independent of the particular widget
		if self.ShowButton.get_active():
			self.ShowButton.set_active( False ) # .ShowButton is a GtkToggleButton, False corresponds to "unpressed"
# Note: It *is* worth checking .ShowButton before setting, because (un)pressing 
# causes .ShowButton to receive both "toggled" and "clicked" signals and .ShowButton's 
# "toggled"/"clicked" handler on_show_button_press (GERGORCALLBACKS.py) does non-trivial graphics.

	def disable_GtkWidgets( self ):
		for e in self.Entries:
			e.disable_GtkWidget()
		if self.ShowButton.get_active():
			self.ShowButton.set_active( False ) # .ShowButton is a GtkToggleButton, False corresponds to "unpressed"
		self.ShowButton.set_sensitive( False ) # .set_sensitive is a general GtkWidget method, independent of the particular widget
# Note: It *is* worth checking .ShowButton before setting, because (un)pressing 
# causes .ShowButton to receive both "toggled" and "clicked" signals and .ShowButton's 
# "toggled"/"clicked" handler on_show_button_press (GERGORCALLBACKS.py) does non-trivial graphics.

class GerGorMatrix():

	"""This class, GerGorMatrix, is responsible for managing the state of the matrix of choices available to the Player. This state is comprised of: the values of each entry, which entries serve as the center of their row's disc, which entry is chosen by the player, which entry was chosen by the player during the previous turn, which rows correspond to discs that were captured, etc. It is also responsible for various related services like: initialization of the matrix, (de)activating the various GtkWidgets that are connected to the matrix entries, performing evolution on each entry, etc. The organization of data is hierarchical: GerGorMatrix contains a list of GerGorMatrixRow, and each GerGorMatrixRow contains a list of GerGorMatrixEntry. In almost all cases, GerGorMatrix partially satisfies commands issued to it and issues similar commands to its GerGorMatrixRows, which then issue similar requests to their GerGorMatrixEntrys if necessary."""

	def __init__( self, size = MATRIXDIM ):
		self.Rows = [ GerGorMatrixRow( size, i ) for i in range( size ) ]

	def __bool__( self ): # boolean context does not trigger this in v2!
		"""BOOLEAN INTERPRETATION of GerGorMatrix: False if all discs are captured (Lose), True otherwise"""
		return any( self.Rows )

	def __nonzero__( self ): # analogue of __bool__ in v2
		"""BOOLEAN INTERPRETATION of GerGorMatrix: False if all discs are captured (Lose), True otherwise"""
		return self.__bool__()

	def __len__( self ):
		"""LENGTH INTERPRETATION of GerGorMatrix: Number of uncaptured rows"""
		return len( list( filter( bool, self.Rows ) ) )

	def align( self, posdiag ):
		"""This method, .align, merely guarantees that each player starts on a different side of the Complex Plane. It should only be called once for each player at the start of the game, before any graphics are displayed."""
		for r in self.Rows:
			r.align( posdiag )

	def evolve( self, numcaptured ):
		"""This method, .evolve, merely instructs each uncaptured instance of GerGorMatrixRow to evolve itself."""
		if numcaptured > 0:
			for _ in range( numcaptured ):
				for r in filter( bool, self.Rows ): # only evolve uncaptured!
					r.evolve( True )
		else:
			for r in filter( bool, self.Rows ): # only evolve uncaptured!
				r.evolve( False )
		self.get_random_GerGorMatrixEntry().negate() # to avoid static end-game, randomly reverse sign of one randomly-chosen entry

	def adrenalize( self, state = True ): # details may change later...
		"""This method, .adrenalize, sets Adrenaline for one disc. According to current rules, this should only be done when this player has only one disc remaining, but .adrenalize does not check this (check it externally with .__len__)."""
		for r in filter( bool, self.Rows ):
			r.adrenalize( state )
			return # deliberate: adrenalize only one

	def set_previous_focus_to_current( self ):
		"""This method, .set_previous_focus_to_current, instructs every row to consider its current choice of entry to be the "previous" choice from now on. This is used to implement the UNDO action: when we start our turn, the choices of entries at that time are the ones to which we should return if a choice is made and then UNDO action is used."""
		for r in filter( bool, self.Rows ): # don't modify captured rows
			r.set_previous_focus_to_current()

	def revert_focus( self ):
		for r in filter( bool, self.Rows ): # don't modify captured rows
			r.revert_focus()

	def update_focus( self, row, col ):
		curfocusofselectedrow = self.Rows[row].get_current_focus()
		for r in filter( bool, self.Rows ): # don't need to update focus of captured rows
			if r.get_current_focus() == col:
				r.set_current_focus( curfocusofselectedrow )
				break # at most one row to update, no need to check others
		self.Rows[row].set_current_focus( col )

	def create_state( self, s = "C" ):
		""" """
		return [ { "center":r.get_center(), "radius":r.get_radius(), "adrenaline":(1 if r.is_adrenalized() else 0), "status":s } for r in filter( bool, self.Rows ) ]

	def get_undo_state( self ):
		"""This method, .get_undo_state, returns the list of dictionaries containing data describing our discs that was true at the *start* of our *previous* turn. In particular, any of our discs that were captured during opponent's most recent turn are *absent* here. It is called by on_accept_button_press (see GERGORCALLBACKS.py) to create the animation required by an ACCEPT action. The underlying list accessed by this method is updated by method .set_undo_state_to_current, which is called by on_matrix_button_press (see GERGORCALLBACKS.py) whenever we select an entry of the matrix."""
		return list( self.UndoState ) # protect this mutable list, return a copy (legal in v2)

	def set_undo_state_to_current( self ):
		self.UndoState = self.create_state()

	def implement_gains( self, awaystate ):
		"""This method, .implement_gains, accepts a LIST of dictionaries containing raw data describing the opponent's discs and checks whether any of theirs were captured by any of ours. Each captured disc is removed from the MUTABLE parameter awaystate. This is deliberate: this parameter is supplied by GerGorComm and is always supposed to represent the most recently known state of the opponent, so discs that are known to be captured should indeed be removed. It is called by finalize_turn. The return is the number of opponent's discs that we captured."""
		todelete = [] # don't actually delete in the loop -- will wreck the iteration
		for ( i, dd ) in enumerate( awaystate ):
			if is_current( dd ):
				for r in filter( bool, self.Rows ): # only uncaptured discs can capture!				
					if check_capture( dd["center"], dd["radius"], r.get_center(), r.get_radius(), r.is_adrenalized() ):
						todelete.append( i )
						break # if dd captured by one r, no need to check if also captured by other r -- terminate inner loop and check next dd
		todelete.reverse() # delete from high to low, otherwise earlier deletions make remaining indices wrong
		for i in todelete:
			del awaystate[i] # deliberate: modifies mutable parameter
		return len( todelete ) # number of captures

	def get_replay_state( self ):
		"""This method, .get_replay_state, returns the collection of raw disc data for our discs that was true at the *end* of our *previous* turn. In particular, any of our discs that were captured during opponent's most recent turn are *still present* here. It is called by replay_timeout (see GERGORCALLBACKS.py) to create the animation required by a REPLAY action. The underlying list accessed by this method is updated by method .set_replay_state_to_current, which is called by finalize_turn (see GERGORCALLBACKS.py) at the end of every turn."""
		return list( self.ReplayState ) # protect this mutable list, return a copy (legal in v2)

	def set_replay_state_to_current( self ):
		self.ReplayState = self.create_state()

	def implement_losses( self, awaystate ):
		"""This method, .implement_losses, accepts a LIST of dictionaries containing raw data describing the opponent's discs and checks whether any of ours were captured by any of theirs. For each captured disc, the corresponding GerGorMatrixRow is instructed to disable itself. It is called by initialize_turn (see GERGORCALLBACKS.py). The parameter must be a LIST, not merely a generator, since it is usually traversed multiple times."""
		numcaptured = 0
		for r in filter( bool, self.Rows ): # only check the ones that aren't already captured
			for dd in filter( isnt_evolved, awaystate ): # filter by isnt_evolved because opponent evolved *after* capturing or failing to capture
				if check_capture( r.get_center(), r.get_radius(), dd["center"], dd["radius"], dd["adrenaline"] ):
					r.capture() # affects filtration in outer loop?
					numcaptured += 1
					break # if r captured by one dd, no need to check if also captured by other dd -- terminate inner loop and check next r
		return numcaptured

	def uncaptured_position( self, i ):
		"""This method, .uncaptured_position, is a simple utility to account for the fact that the position of a row within the Matrix is different from the position of its corresponding disc in the list that is usually passed around for communication and image purposes. For example, when the SHOW button is pressed, it knows its corresponding row within the Matrix. But to alter the corresponding disc in the paint queue, the row's position among the uncaptured rows is necessary."""
		return i - len( [ x for x in self.Rows[:i] if not bool( x ) ] )

	def get_random_GerGorMatrixEntry( self, allowcaptured = False, allowfocus = False ):
		"""This method, .get_random_GerGorMatrixEntry, returns a randomly selected GerGorMatrixEntry member from within the matrix, with the possibility to exclude rows corresponding to captured discs or entries that are the current focus of their row."""
		ggr = random.choice( self.Rows if allowcaptured else list( filter( bool, self.Rows ) ) )
		return ggr.get_random_GerGorMatrixEntry( allowfocus )

	def set_GtkWidgets( self, widget, row, col, showbutton ):
		"""This method, .set_GtkWidgets, associates (by delegation) the necessary GtkWidgets to each row and/or entry of the matrix. Hereafter, each row and/or entry of the matrix (more precisely, each instance of GerGorMatrixRow and/or GerGorMatrixEntry) is responsible for manipulating its own GtkWidget(s) after receiving the appropriate command from GerGorMatrix."""
		self.Rows[row].set_GtkWidgets( widget, col, showbutton )

	def refresh_GtkWidgets( self ):
		for r in filter( bool, self.Rows ): # don't modify captured rows
			r.refresh_GtkWidgets()

	def enable_GtkWidgets( self ):
		for r in filter( bool, self.Rows ): # don't enable captured rows
			r.enable_GtkWidgets()

	def disable_GtkWidgets( self ):
		for r in self.Rows: # disabling captured rows ok
			r.disable_GtkWidgets()

