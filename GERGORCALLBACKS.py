# This file defines all the signal-handlers needed by the GUI constructed in 
# GERGOR.py, some functions used as GTK+ timeouts, and a few other "helper" functions.


import random # NOT SEEDED HERE!

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib

from gergormatrix import GerGorMatrix
from gergorcomm import GerGorComm
from gergorimage import GerGorImage
from gergorpaintable import GerGorPaintable
from gergoranimation import GerGorAnimation

from GERGORCONFIG import is_current, isnt_evolved, check_capture
from GERGORCONFIG import STATUSBADFILE, STATUSWIN, STATUSLOSS, STATUSBEGIN, STATUSREPLAYING, STATUSACTION, STATUSANIMATING, STATUSOPPTURN, STATUSTIMEREMAININGFMT
from GERGORCONFIG import COMMTIMEOUTFREQ, ANIMTIMEOUTFREQ, TURNLIMITCOUNT, TURNLIMITFREQ, AUTOPILOTTHRESHOLD, MATRIXADRENALINERATE


# global variables used to communicate high-level game information
Ggameover = False # self-explanatory
GstandbyID = None # used to allow manual disconnection of standby_timeout (e.g. upon Quit)
GcountdownID = None # used to allow manual disconnection of countdown_timeout (e.g. upon Quit)
GreplayID = None # used to allow manual disconnection of replay_timeout (e.g. upon Quit)
GanimationID = None # used to allow manual disconnection of animation_timeout (e.g. upon Quit)


def on_connect_button_press( self, loc, plane, matrix, comm, image, bdict, slabel ):
# can change game's state from "Entered location" to "Waiting for Opponent"
# deliberately disable: LBOX, CONNECT
# deliberately enable: nothing
# can also change game's state from "Entered location" to "Just launched" (if bad location given)
# deliberately disable: nothing
# deliberately enable: nothing
	if loc.get_text() == "sup":
		loc.set_text( "" )
		slabel.set_label( "nuthin... sup with you?" )
		return
	if not comm.set_write_location( loc.get_text() ): # GerGorComm rejected location, likely player-error, do nothing except notify player and wait for better
		loc.set_text( "" ) # for player's convenience, erase whatever was in the GtkEntry
		slabel.set_label( STATUSBADFILE )
		return
	self.set_sensitive( False ) # self == CONNECT, for remainder of game, will not need this GtkWidget
	loc.set_sensitive( False ) # loc == LBOX, for remainder of game, will not need this GtkWidget
	matrix.align( not comm.is_first() ) # use order of play to decide who is on positive side of plane (comm.set_write_location necessary before comm.is_first!)
	matrix.refresh_GtkWidgets()
	if comm.is_first(): # wait for data from opponent, who plays second and will therefore auto-PASS
		slabel.set_label( STATUSOPPTURN )
		global GstandbyID # may need to manually disconnect later -- record ID
		GstandbyID = GLib.timeout_add( COMMTIMEOUTFREQ, standby_timeout, plane, matrix, comm, image, bdict, slabel )
	else:
		bdict["Pass"].clicked() # opponent is first -- defer to opponent and simultaneously send our data by simulating PASS action


def standby_timeout( plane, matrix, comm, image, bdict, slabel ):
	"""This function, standby_timeout, is registered with GTK+ as a timeout at the end our turn and listens for communication from opponent, which will occur at the end of opponent's turn and signals that we should begin our turn."""
	if not comm: # GerGorComm.__bool__() indicates whether data is available from opponent
		return True # tell GTK+ to continue running timeout -- there is no data yet
	global GstandbyID
	GLib.source_remove( GstandbyID ) # see below for explanation
	GstandbyID = None
	initialize_turn( plane, matrix, comm, image, bdict, slabel )
	return False # because of complex intertwining of GTK+ timeouts, this return *cannot* properly disconnect standby_timeout in certain situations


def initialize_turn( plane, matrix, comm, image, bdict, slabel ):
	"""This function, initialize_turn, is called at the beginning of every turn, immediately after standby_timeout detects data sent from opponent."""
	initialize_turn.numturns += 1
	comm.receive()
	if initialize_turn.numturns < 2: # still exchanging info, not a "real" turn
		if not comm.is_first(): # if we play second, nice to see the initial positions while waiting for opponent to finish first "real" turn
			GerGorPaintable( matrix.create_state(), [ d for d in comm.get_newest_data() if is_current( d ) ] ).paint( image, plane )
		bdict["Pass"].clicked() # simulate that both players PASS their first turn, to be sure data is shared
		return # this turn is for "setup", don't continue turn
	global Ggameover
	if not comm.get_newest_data(): # opponent's data is empty, which indicates WIN for us
# changes game's state from "Waiting for Opponent" to "Win"
# deliberately disable: nothing
# deliberately enable: nothing
		Ggameover = True
		slabel.set_label( STATUSWIN )
		return # WIN, no need to further initialize or do anything else
	if initialize_turn.numturns >= ( 3 if comm.is_first() else 2 ): # captures only allowed if opponent played (1st turn if 2nd player but 2nd turn if first player)
		matrix.implement_losses( comm.get_newest_data() ) # note: GerGorMatrix.implement_losses filters by "not evolved"
	matrix.set_previous_focus_to_current() # after turn begins, UNDO means to restore whatever state matrix is in now
	if ( len( matrix ) == 1 ) and ( random.random() < MATRIXADRENALINERATE ):
		matrix.adrenalize()
	matrix.refresh_GtkWidgets() # update the matrix GUI to express the new situation
	if not matrix: # GerGorMatrix.__bool__() indicates whether any rows are uncaptured... if not, LOSS
		Ggameover = True
		bdict["Autopilot"].set_active( False ) # unpress AUTO, merely for appearance (note: this causes bdict["Autopilot"] to receive both "clicked" and "toggled" signals)
		slabel.set_label( STATUSLOSS ) # change to GtkMessageDialog?
		comm.send( None ) # when opponent receives this "stub" data, will trigger WIN
		# deliberate: no return (want to see opponent's turn even if LOSS)
	if initialize_turn.numturns >= ( 3 if comm.is_first() else 2 ): # first "real" turn *for which there is something to replay* (1st turn if 2nd player but 2nd turn if first player)
# changes game's state from "Waiting for Opponent" to "Replaying Opponent"
# deliberately disable: QUIT
# deliberately enable: nothing
		bdict["Replay"].clicked() # this will disable QUIT
	else: # control only reaches here if we play first *and* this is our first "real" turn (don't do "full" replay)
		GerGorPaintable( matrix.create_state(), [ d for d in comm.get_newest_data() if is_current( d ) ] ).paint( image, plane )
		matrix.enable_GtkWidgets() # this enables ENTRIES/SHOW
		# don't enable Replay on this very special turn
		bdict["Pass"].set_sensitive( True )
		bdict["Autopilot"].set_sensitive( True )
		bdict["Quit"].set_sensitive( True )
		slabel.set_label( STATUSBEGIN )
	if not Ggameover: # if LOSS then no reason to start Timer
# changes game's state from "Waiting for Opponent" to "Waiting for Choice (Autopilot *)"
# deliberately disable: nothing
# deliberately enable: REPLAY, PASS, AUTO, ENTRIES/SHOW (done indirectly by previous if/else clause)
		global GcountdownID # may need to manually disconnect later -- record ID
		GcountdownID = GLib.timeout_add( TURNLIMITFREQ, countdown_timeout, matrix, comm, bdict, slabel )


def countdown_timeout( matrix, comm, bdict, slabel ):
	"""This function, countdown_timeout, manages both the Timer (maximum amount of time allowed for each turn) and the Autopilot (virtual player). At the beginning of every turn (more precisely, at the end of the function initialize_turn), countdown_timeout is registered with GTK+ as a timeout and thereafter is run periodically. The Timer should "pause" if an animation is playing, so countdown_timeout does nothing in that case except maintain its own status as a timeout. Otherwise, either time expired or not. If time expired, countdown_timeout forces the PASS button to be pressed (it is possible that time expired after the Player clicked a button in the Matrix but before clicking ACCEPT, so countdown_timeout also clicks UNDO). Otherwise, countdown_timeout either completes the turn via Autopilot or merely displays the remaining time and decrements the Timer. It is important to wait a short amount of time after the start of the turn before performing Autopilot: the Player needs opportunity to deactivate Autopilot, and it is generally a better experience for moves not to happen so rapidly."""
	if countdown_timeout.isanimating: # "pause" Timer during animation by returning BEFORE decrement...
		return True # ... but tell GTK+ to continue running this timeout
	global GcountdownID
	if countdown_timeout.timer > 0:
		if ( countdown_timeout.timer <= AUTOPILOTTHRESHOLD ) and ( bdict["Autopilot"].get_active() ): # bdict["Autopilot"] is a GtkToggleButton
			if do_autopilot_select( matrix, comm ):
				bdict["Accept"].clicked() # this will indirectly cause countdown_timeout to be disconnected
			else:
				bdict["Pass"].clicked() # this will indirectly cause countdown_timeout to be disconnected
			GcountdownID = None # guarantee that manual disconnection of already-disconnected countdown_timeout is not attempted later
			return False # tells (or reaffirms?) GTK+ we don't want to continue timeout, because turn is finished
		slabel.set_label( STATUSTIMEREMAININGFMT % ((countdown_timeout.timer*TURNLIMITFREQ)//1000) )
		countdown_timeout.timer -= 1
		return True # tell GTK+ to continue running timeout, since turn still active
	if bdict["Undo"].get_sensitive(): # possible that player made a choice but did not yet ACCEPT when timer ended...
		bdict["Undo"].clicked() # ... so force-UNDO before force-PASS
	bdict["Pass"].clicked() # time expired! force-PASS (will indirectly cause countdown_timeout to be disconnected)
	GcountdownID = None # guarantee that manual disconnection of already-disconnected countdown_timeout is not attempted later
	return False # tells (or reaffirms?) GTK+ we don't want to continue timeout, because turn is finished


def on_autopilot_button_press( self, matrix, bdict ):
# can change game's state from "Waiting for choice (Autopilot ON)" to "Waiting for choice (Autopilot OFF)"
# deliberately disable: REPLAY, PASS, ENTRIES/SHOW
# deliberately enable: nothing
# can also change game's state from "Waiting for choice (Autopilot OFF)" to "Waiting for choice (Autopilot ON)"
# deliberately disable: REPLAY, PASS, ENTRIES/SHOW
# deliberately enable: nothing
	if( self.get_active() ): # self == AUTO (True <=> Autopilot ON)
		matrix.disable_GtkWidgets() # this disables ENTRIES/SHOW
		bdict["Replay"].set_sensitive( False )
		bdict["Pass"].set_sensitive( False )
	else:
		global Ggameover
		if not Ggameover: # initialize_turn will force-unpress AUTO at the end of the game, so be sure not to enable these in that case
			matrix.enable_GtkWidgets() # this disables ENTRIES/SHOW
			bdict["Pass"].set_sensitive( True )
		bdict["Replay"].set_sensitive( True )


def do_autopilot_select( matrix, comm ):
	"""This function, do_autopilot_select, is responsible for performing a move without Player's input. Formally, it is responsible simply for clicking a button in the Matrix and notifying its caller that ACCEPT should be done (return True), or notifying its caller that PASS is the best option (return False). In this prototype, a random button is clicked unless one of the opponent's discs happens already to be inside one of ours (lucky!). In a future version of the game, the Autopilot may be more intelligent."""
# The quadratic search done next could be made more efficient, e.g. sorting first by radius and continue-ing when capture is radially impossible. However, the number of iterations for each loop will always be extremely tiny (equal to GERGORCONFIG.MATRIXDIM), so the extra effort and complexity is not justified.
	for hdd in matrix.create_state():
		for add in filter( is_current, comm.get_newest_data() ):
			if check_capture( add["center"], add["radius"], hdd["center"], hdd["radius"], hdd["adrenaline"] ):
				return False # notifies caller to PASS move
	matrix.get_random_GerGorMatrixEntry().get_GtkWidget().clicked()
	return True # notifies caller to ACCEPT move


def on_show_button_press( self, row, plane, matrix, comm, image ):
# can only change game's state from "Waiting for choice (Autopilot *)" to "Waiting for choice (Autopilot same *)"
# deliberately disable: nothing (but unpress any other SHOW)
# deliberately enable: nothing
	if self is not on_show_button_press.previously_selected:
		if on_show_button_press.previously_selected is not None: # first use of SHOW this turn
			on_show_button_press.previously_selected.set_active( False ) # note: this causes on_show_button_press.previously_selected to receive both "toggled" and "clicked" signals
		on_show_button_press.previously_selected = self
	s = GerGorPaintable( matrix.create_state(), [ d for d in comm.get_newest_data() if is_current( d ) ] )
	s.distinguish( matrix.uncaptured_position( row ), self.get_active() )
	s.paint( image, plane )
# It is important that on_matrix_button_press deactivates all SHOW buttons after the player makes a choice.
# Otherwise, the player can view the exact result of any potential move, eliminating much of the difficulty.


def on_matrix_button_press( self, matrix, row, col, bdict, slabel ):
	"""There is a square array of buttons, each representing an entry in the Matrix. The buttons indicate various Real Numbers and are each decorated to also indicate whether the entry contributes to the center or radius of the disc corresponding to that row of the Matrix. Clicking any of these buttons causes this function, on_matrix_button_press, to be called with arguments indicating which button was clicked. This function changes the internal state of the Matrix to reflect the player's choice, updates the GUI to reflect those changes, and toggles various buttons appropriate to the next phase of the turn."""
# can only change game's state from "Waiting for choice (Autopilot OFF)" to "Chose, awaiting confirmation"
# deliberately disable: REPLAY, PASS, AUTO, ENTRIES/SHOW
# deliberately enable: UNDO, ACCEPT
	matrix.disable_GtkWidgets() # this disables ENTRIES/SHOW
	bdict["Autopilot"].set_sensitive( False )
	bdict["Replay"].set_sensitive( False )
	bdict["Pass"].set_sensitive( False )
	matrix.set_undo_state_to_current() # our state *before* current turn's move (need for animation that happens upon ACCEPT)
	matrix.update_focus( row, col )
	matrix.refresh_GtkWidgets()
	bdict["Undo"].set_sensitive( True )
	bdict["Accept"].set_sensitive( True )
	slabel.set_label( STATUSACTION )


def on_undo_button_press( self, matrix, comm, bdict, slabel ):
# can only change game's state from "Chose, awaiting confirmation" to "Waiting for choice (Autopilot OFF)"
# deliberately disable: ACCEPT, UNDO
# deliberately enable: REPLAY, PASS, AUTO, ENTRIES/SHOW
	self.set_sensitive( False ) # self == UNDO
	bdict["Accept"].set_sensitive( False )
	matrix.revert_focus()
	matrix.refresh_GtkWidgets()
	matrix.enable_GtkWidgets() # this enables ENTRIES/SHOW
	bdict["Pass"].set_sensitive( True )
	if initialize_turn.numturns >= ( 3 if comm.is_first() else 2 ): # no need for replay until opponent did something!
		bdict["Replay"].set_sensitive( True )
	bdict["Autopilot"].set_sensitive( True )
	slabel.set_label( STATUSBEGIN )


def on_replay_button_press( self, plane, matrix, comm, image, bdict, slabel ):
# can change game's state from "Waiting for choice (Autopilot *)" to "Replaying Opponent"
# deliberately disable: REPLAY, PASS, QUIT, AUTO, ENTRIES/SHOW
# deliberately enable: nothing
# can also change game's state from "Loss" to "Replaying Opponent"
# deliberately disable: REPLAY, QUIT
# deliberately enable: nothing
	countdown_timeout.isanimating = True # indicates to countdown_timeout that Timer should *not* decrement (busy animating replay)
	self.set_sensitive( False ) # self == REPLAY, don't allow REPLAY while replaying...
	global Ggameover
	if not Ggameover:
		bdict["Autopilot"].set_sensitive( False )
		matrix.disable_GtkWidgets() # this disables ENTRIES/SHOW
		bdict["Pass"].set_sensitive( False )
	bdict["Quit"].set_sensitive( False ) # not unreasonable to disable QUIT during animation
	animation = GerGorAnimation( filter( is_current, comm.get_previous_data() ), filter( isnt_evolved, comm.get_newest_data() ) )
	slabel.set_label( STATUSREPLAYING )
	global GreplayID # may need to manually disconnect later -- record ID
	GreplayID = GLib.timeout_add( ANIMTIMEOUTFREQ, replay_timeout, plane, matrix, comm, image, animation, bdict, slabel )


def replay_timeout( plane, matrix, comm, image, animation, bdict, slabel ):
# can change game's state from "Replaying Opponent" to "Waiting for choice (Autopilot *)"
# deliberately disable: nothing
# deliberately enable: REPLAY, PASS, AUTO, QUIT, ENTRIES/SHOW
# can also change game's state from "Replaying Opponent" to "Loss"
# deliberately disable: nothing
# deliberately enable: REPLAY, QUIT
	if animation: # GerGorAnimation.__bool__() indicates whether more frames are available
		GerGorPaintable( matrix.get_replay_state(), animation.next_frame() ).paint( image, plane ) # arguments already filtered in on_replay_button_press
		return True # tell GTK+ to continue running this timeout until there are no more frames
	GerGorPaintable( matrix.create_state(), [ d for d in comm.get_newest_data() if is_current( d ) ] ).paint( image, plane )
	global Ggameover
	if Ggameover: # player can REPLAY even after LOSS -- reprint LOSS message (if WIN then REPLAY disabled and control never reaches here)
		slabel.set_label( STATUSLOSS )
		bdict["Replay"].set_sensitive( True )
	else:
		if not bdict["Autopilot"].get_active():
			matrix.enable_GtkWidgets() # this enables ENTRIES/SHOW
			bdict["Pass"].set_sensitive( True )
			bdict["Replay"].set_sensitive( True )
		bdict["Autopilot"].set_sensitive( True )
		slabel.set_label( STATUSBEGIN )
	bdict["Quit"].set_sensitive( True ) # disabled QUIT for animation, enable now that animation is finished
	countdown_timeout.isanimating = False # indicates to countdown_timeout that Timer *is* allowed to decrement (replay animation is finished)
	global GreplayID
	GreplayID = None
	return False # tell GTK+ to discontinue this timeout -- replay animation is finished


def on_accept_button_press( self, plane, matrix, comm, image, bdict, slabel ):
# can only change game's state from "Chose, awaiting confirmation" to "Animating self"
# deliberately disable: ACCEPT, UNDO, QUIT
# deliberately enable: nothing
# note: Autopilot's ACCEPT is same as player's ACCEPT, including that an entry in the matrix was actually clicked (simulated by GtkButton.clicked)... 
# ... hence, don't need to disable REPLAY, PASS, AUTO, ENTRIES/SHOW because done already by on_matrix_button_press
	countdown_timeout.isanimating = True # indicates to countdown_timeout that Timer should *not* decrement (busy animating end-of-turn)
	self.set_sensitive( False ) # self == ACCEPT
	bdict["Undo"].set_sensitive( False )
	animation = GerGorAnimation( matrix.get_undo_state(), matrix.create_state() )
	slabel.set_label( STATUSANIMATING )
	bdict["Quit"].set_sensitive( False ) # not unreasonable to disable QUIT during animation
	global GanimationID # may need to manually disconnect later -- record ID
	GanimationID = GLib.timeout_add( ANIMTIMEOUTFREQ, animation_timeout, plane, matrix, comm, image, animation, bdict, slabel )


def animation_timeout( plane, matrix, comm, image, animation, bdict, slabel ):
# can only change game's state from "Animating self" to "Waiting for Opponent"
# deliberately disable: nothing
# deliberately enable: QUIT
	if animation: # GerGorAnimation.__bool__() indicates whether more frames are available
		GerGorPaintable( animation.next_frame(), [ d for d in comm.get_newest_data() if is_current( d ) ] ).paint( image, plane )
		return True # tell GTK+ to continue running this timeout until there are no more frames
	# disconnect animation_timeout early because of finalize_turn starts another timeout?
	finalize_turn( plane, matrix, comm, image, bdict, slabel ) # this will enable QUIT
	countdown_timeout.isanimating = False
	global GanimationID
	GanimationID = None
	return False # tell GTK+ to discontinue this timeout -- end-of-turn animation is finished


def on_pass_button_press( self, plane, matrix, comm, image, bdict, slabel ):
# can only change game's state from "Waiting for choice (Autopilot OFF)" to "Waiting for Opponent"
# should be disabled: REPLAY, PASS, AUTO, ENTRIES/SHOW
# should be enabled: QUIT
	self.set_sensitive( False ) # self == PASS
	bdict["Autopilot"].set_sensitive( False )
	bdict["Replay"].set_sensitive( False )
	matrix.disable_GtkWidgets() # this disables ENTRIES/SHOW
	finalize_turn( plane, matrix, comm, image, bdict, slabel ) # this will enable QUIT


def finalize_turn( plane, matrix, comm, image, bdict, slabel ):
	"""This function, finalize_turn, is called at the end of every turn, regardless of ACCEPT or PASS. Note that it is necessary to update the graphics even if the player PASSed: It sometimes happens that a player can capture by simply PASSing, usually due to a miscalculation by the opponent, and the capture must be depicted."""
	global GcountdownID
	if GcountdownID is not None:
		GLib.source_remove( GcountdownID )
		GcountdownID = None # guarantee that no attempt is made to manually disconnect countdown_timeout later -- happened previous line
	countdown_timeout.timer = TURNLIMITCOUNT # reset the Timer
	preevolvedstate = matrix.create_state( "R" ) # need to send opponent state prior to evolution, for Replay and Capture purposes
	if initialize_turn.numturns >= 2: # "real" turn
		numcaptured = matrix.implement_gains( comm.get_newest_data_mutable() ) # note: GerGorMatrix.implement_gains filters by "yes evolved"
		matrix.evolve( numcaptured )
		GerGorPaintable( matrix.create_state(), [ d for d in comm.get_newest_data() if is_current( d ) ] ).paint( image, plane ) # note: comm's data was modified above
		matrix.refresh_GtkWidgets() # show the post-evolution numbers on the matrix
	matrix.set_replay_state_to_current() # our state at end of our current turn, *before* opponent next captures (need for REPLAY during our next turn)
	comm.send( preevolvedstate + matrix.create_state() ) # opponent needs to know pre- and post-evolution states
	if len( matrix ) == 1: # important to do comm.send before this: opponent needs to depict Adrenaline
		matrix.adrenalize( False )
	slabel.set_label( STATUSOPPTURN )
	bdict["Quit"].set_sensitive( True ) # always allow QUIT while waiting for opponent
	global GstandbyID # may need to manually disconnect later -- record ID
	GstandbyID = GLib.timeout_add( COMMTIMEOUTFREQ, standby_timeout, plane, matrix, comm, image, bdict, slabel ) # wait for opponent to finish turn and send data


def on_quit_button_press( self, gdkevent, comm, gtkwin ):
	"""This function, on_quit_button_press, is connected to the main window's delete-event and to the QUIT button. Primarily, it simply sends 'stub' data to the opponent, which the opponent will interpret as a WIN when it is detected by standby_timeout, and concludes GTK+ normally. However, this close/Quit may occur while GTK+ is running timeouts. For example, close/Quit while it is the opponent's turn occurs while standby_timeout is running. Close/Quit while it is our turn often occurs while countdown_timeout is running, and/or while animation_timeout or replay_timeout are running. Those active timeouts will (always?) prevent garbage-collection for their arguments, potentially then also leading to leftover GerGorComm temporary file(s), etc. For this reason, handles for those timeouts are stored (in global variables) while they are running, and they are forcibly disconnected from GTK+ here if necessary."""
	global GstandbyID, GcountdownID, GreplayID, GanimationID
	for ID in ( GstandbyID, GcountdownID, GreplayID, GanimationID ):
		if ID is not None:
			GLib.source_remove( ID )
	comm.send( None )
	if gtkwin is not None:
		gtkwin.destroy()

