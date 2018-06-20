# This is the "main" script: by launching it in Python, a GUI is constructed, 
# the components of that GUI are made receptive to various user input via 
# keyboard/mouse (i.e. handlers for appropriate signals are registered with 
# each widget), various other things are initialized, and GTK+'s "main loop" 
# is initiated to receive and dispatch user input.


import os, sys

import random

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from GERGORCONFIG import GUILABELSMYCONN, GUILABELSOPPONENTCONN, GUILABELSCONNECT, GUILABELSSTATUS, GUILABELSACTIONS, GUILABELSMATRIX, GUIICONPREFIX, STATUSALONE, MATRIXDIM, MATRIXUNKNOWNENTRYPANGOFMT, TURNLIMITCOUNT
from GERGORCALLBACKS import on_connect_button_press, on_matrix_button_press, on_show_button_press, on_replay_button_press, on_pass_button_press, on_undo_button_press, on_accept_button_press, on_quit_button_press
from GERGORCALLBACKS import on_autopilot_button_press, countdown_timeout, initialize_turn
from gergormatrix import GerGorMatrix
from gergorcomm import GerGorComm
from gergorimage import GerGorImage


random.seed() # according to documentation, will use system time if no arguments


# communication stuff
C = GerGorComm()

homelabel = Gtk.Label( C.get_read_location() ) # GerGorComm decides what a player's connection info is, display it to the player
homelabel.set_selectable( True ) # allow the player to copy, and presumably then paste somewhere, own connection info
homelabelframe = Gtk.Frame( label = GUILABELSMYCONN ) # purpose is purely visual
homelabelframe.add( homelabel )

opponentloc = Gtk.Entry()
opponentlocframe = Gtk.Frame( label = GUILABELSOPPONENTCONN ) # purpose is purely visual
opponentlocframe.add( opponentloc )

connectbutton = Gtk.Button.new_with_label( GUILABELSCONNECT )

statuslabel = Gtk.Label( STATUSALONE )
statuslabel.set_selectable( False ) # don't need to allow copy/paste of this
statuslabelframe = Gtk.Frame( label = GUILABELSSTATUS ) # purpose is purely visual
statuslabelframe.add( statuslabel )


# image stuff
I = GerGorImage()

plane = Gtk.Image()
planeframe = Gtk.Frame() # purpose is purely visual
planeframe.add( plane )


# gameplay buttons
buttons = {} # dictionary of buttons is more convenient to pass throughout GERGORCALLBACKS.py
buttons["Replay"] = Gtk.Button.new_with_label( "Replay" )
buttons["Pass"] = Gtk.Button.new_with_label( "Pass" )
buttons["Undo"] = Gtk.Button.new_with_label( "Undo" )
buttons["Accept"] = Gtk.Button.new_with_label( "Accept" )
buttons["Quit"] = Gtk.Button.new_with_label( "QUIT" )
buttons["Autopilot"] = Gtk.ToggleButton.new_with_label( "~AUTO~" ) # Toggle!

buttons["Replay"].set_sensitive( False )
buttons["Pass"].set_sensitive( False )
buttons["Undo"].set_sensitive( False )
buttons["Accept"].set_sensitive( False )
buttons["Quit"].set_sensitive( True ) # even though player can close program by other means, nice to allow QUIT before genuinely starting game
buttons["Autopilot"].set_sensitive( False ) # note: in all situations, AUTO should be sensitive if and only if PASS is sensitive

buttongrid = Gtk.Grid()
buttongrid.attach( buttons["Replay"], 0, 0, 1, 1 )
buttongrid.attach( buttons["Pass"], 0, 1, 1, 1 )
buttongrid.attach( buttons["Undo"], 0, 2, 1, 1 )
buttongrid.attach( buttons["Accept"], 0, 3, 1, 1 )
buttongrid.attach( buttons["Quit"], 0, 4, 1, 1 )
buttongrid.attach( buttons["Autopilot"], 0, 5, 1, 1 )

buttongridframe = Gtk.Frame( label = GUILABELSACTIONS ) # purpose is purely visual
buttongridframe.add( buttongrid )


# matrix stuff
M = GerGorMatrix()
matrixgrid = Gtk.Grid()
for i in range( MATRIXDIM ):
	showbutton = Gtk.ToggleButton.new_with_label( "SHOW" ) # Toggle!
	showbutton.connect( "toggled", on_show_button_press, i, plane, M, C, I ) # need to connect here... want/will lose button after this loop
	for j in range( MATRIXDIM ):
		button = Gtk.Button.new_with_label( "?" )
		button.get_child().set_markup( MATRIXUNKNOWNENTRYPANGOFMT )
		button.connect( "clicked", on_matrix_button_press, M, i, j, buttons, statuslabel ) # need to connect here... want/will lose buttons after this loop
		M.set_GtkWidgets( button, i, j, showbutton )
		matrixgrid.attach( child = button, top=i, left=j, height=1, width=1 ) # kwargs avoid "row vs. col" confusion
	matrixgrid.attach( child = showbutton, top=i, left=MATRIXDIM, height=1, width=1 )
M.disable_GtkWidgets()

matrixgridframe = Gtk.Frame( label = GUILABELSMATRIX ) # purpose is purely visual
matrixgridframe.add( matrixgrid )


# embedding components into a big GtkGrid and then embedding the GtkGrid into the main GtkWindow
gamegrid = Gtk.Grid()
gamegrid.attach( homelabelframe, left=0, top=0, width=2, height=1 )
gamegrid.attach( opponentlocframe, left=0, top=1, width=1, height=1 )
gamegrid.attach( connectbutton, left=1, top=1, width=1, height=1 )
gamegrid.attach( planeframe, left=0, top=2, width=2, height=1 )
gamegrid.attach( matrixgridframe, left=0, top=3, width=1, height=1 )
gamegrid.attach( buttongridframe, left=1, top=3, width=1, height=1 )
gamegrid.attach( statuslabelframe, left=0, top=4, width=2, height=1 )

gamewin = Gtk.Window( title = "GerGor" )
gamewin.add( gamegrid )

GUIICONPATH = os.path.join( sys.path[0], GUIICONPREFIX + os.extsep + "jpg" ) # correctly splice together whatever directory contains GERGOR.py and image filename
if os.path.isfile( GUIICONPATH ): # if the icon exists (why wouldn't it?) then make it the program's "official" icon
	gamewin.set_icon_from_file( GUIICONPATH )


# connecting events/signals (note: for simulating mouseclicks (e.g. to implement Autopilot), need "clicked" signal because .emit doesn't seem to work...)
connectbutton.connect( "clicked", on_connect_button_press, opponentloc, plane, M, C, I, buttons, statuslabel )
buttons["Replay"].connect( "clicked", on_replay_button_press, plane, M, C, I, buttons, statuslabel )
buttons["Pass"].connect( "clicked", on_pass_button_press, plane, M, C, I, buttons, statuslabel  )
buttons["Undo"].connect( "clicked", on_undo_button_press, M, C, buttons, statuslabel )
buttons["Accept"].connect( "clicked", on_accept_button_press, plane, M, C, I, buttons, statuslabel )
buttons["Autopilot"].connect( "toggled", on_autopilot_button_press, M, buttons )
buttons["Quit"].connect( "clicked", on_quit_button_press, None, C, gamewin ) # argument None provided to allow event-handler on_quit_button_press to be used as signal-handler also
gamewin.connect( "delete-event", on_quit_button_press, C, None )
gamewin.connect( "destroy", Gtk.main_quit )


# initialize "static" local variables for functions in GERGORCALLBACKS.py
on_show_button_press.previously_selected = None
countdown_timeout.timer = TURNLIMITCOUNT 
countdown_timeout.isanimating = False
initialize_turn.numturns = 0 # used to distinguish information-sharing turns from "real" turns


gamewin.show_all() # fully initializes all GtkWidgets recursively


I.reset()
I.flush( plane ) # I think it's safer for this to occur after gamewin.show_all, since some aspects of the plane's initialization are not done until then


Gtk.main()

