# This file, GERGORCONFIG.py, specifies most details of the game in one convenient place.
# Most strings, sizes, speeds, and colors are specified here.
# Some calculations are also defined here, and exceptions are noted.
# Much customization can be done using only this file.


from PIL import ImageColor


GUILABELSMYCONN = "My Connection Info"
GUILABELSOPPONENTCONN = "Opponent's Connection Info"
GUILABELSCONNECT = "Connect"
GUILABELSSTATUS = "Game Status"
GUILABELSACTIONS = "Actions"
GUILABELSMATRIX = "Matrix"

GUIICONPREFIX = "GERGORICON"


STATUSALONE = "Supply opponent's location..."
STATUSBADFILE = "Invalid file... " + STATUSALONE.lower()
STATUSWIN = "YOU WIN!"
STATUSLOSS = "YOU LOSE!"
STATUSBEGIN = "Choose entry or Pass..."
STATUSACTION = "Entry chosen, awaiting action..."
STATUSANIMATING = "Executing choice..."
STATUSOPPTURN = "Waiting for opponent..."
STATUSREPLAYING = "Replaying opponent's turn..."
STATUSTIMEREMAININGFMT = STATUSBEGIN + " (time remaining: %d seconds)"


MATRIXDIM = 9 # number of rows/columns in the matrix
MATRIXUNKNOWNENTRYPANGOFMT = "<span font_size=\"large\">&#10068;</span>" # what to display when a matrix entry is unknown (Pango Markup + HTML code, passed into a GtkLabel)
MATRIXENTRYRANGE = 50 # matrix entries are randomly generated (by GerGorMatrixEntry) and have absolute value below this
MATRIXMINSIGNS = int( round( MATRIXDIM / 3.0 ) ) # minimum number of positive and negative entries to guarantee at start
MATRIXCAPTUREDPANGOFMT = "<span font_size=\"large\">&#9785;</span>" # how entries in a row appear when its disc is captured (Pango Markup + HTML code, passed into a GtkLabel)
MATRIXCENTRALENTRYPANGOFMT = "<b>%.1f</b>" # how a matrix entry appears when it serves as center (Pango Markup passed into a GtkLabel)
MATRIXRADIALENTRYPANGOFMT = "|%.1f|" # how a matrix entry appears when it contributes to radius (Pango Markup passed into a GtkLabel)
MATRIXGROWTHFACTOR = 1.03 # other details regarding growth/decay are found in the .evolve methods of GerGorMatrix.py
MATRIXDECAYFACTOR = 0.99 # other details regarding growth/decay are found in the .evolve methods of GerGorMatrix.py
MATRIXADRENALINERATE = 0.2 # if a player has only one disc remaining, probability that the disc will become Adrenalized
MATRIXRADIUSPOSRANGE = 2 # how many entries on each side of selected contribute to radius (actual calculation of radius in GerGorMatrixRow.get_radius)
MATRIXRADIUSWEIGHT = 1.0/MATRIXDIM # seems like a good choice of "weight" in general (actual calculation of radius in GerGorMatrixRow.get_radius)
def check_capture( defendc, defendr, attackc, attackr, adrenalized ): # rules regarding Adrenaline may change later...
	return ( ( defendc <= attackc + attackr ) and ( defendc >= attackc - attackr ) ) if adrenalized else ( ( defendc + defendr <= attackc + attackr ) and ( defendc - defendr >= attackc - attackr ) )


COMMTIMEOUTFREQ = 200 # how often to check if data is available from the opponent (standby_timeout runs every COMMTIMEOUTFREQ milliseconds)
COMMPREFIX = "GERGOR" # prepend this to temporary files on the local disk
COMMSUFFIX = "gergor" # extension used by GerGorComm for the communication file (six-character extensions are ok on all systems, right?)
COMMRANDMIN = 100000000 # helps GerGorComm to generate a random ID with exactly 10 digits
COMMSTUB = "gergor" # token that distinguishes between file prior to communication and a file containing empty communication
def is_current( dd ):
	return bool( "C" in dd["status"] )
def isnt_evolved( dd ):
	return bool( "R" in dd["status"] )


TURNLIMITCOUNT = 90 # "abstract" counter used to implement Timer (countdown_timeout runs TURNLIMITCOUNT times and ordinarily decrements by 1 each time)
TURNLIMITFREQ = 500 # how often to decrement the "abstract" Timer (countdown_timeout runs every TURNLIMITFREQ milliseconds)
# thus, actual time allowed for one turn is TURNLIMITCOUNT*TURNLIMITFREQ/1000 seconds


ANIMNUMFRAMES = 64 # number of distinct frames to use in each animation (GerGorAnimation interpolates any start/end pair into a sequence of ANIMNUMFRAMES+1 images)
ANIMTIMEOUTFREQ = 75 # how long to wait before displaying the next frame of an animation (replay_timeout, animation_timeout display one every ANIMTIMEOUTFREQ milliseconds)
# thus, actual time from start to finish of one animation is something like ANIMNUMFRAMES*ANIMTIMEOUTFREQ/1000 seconds
# note that increasing (resp. decreasing) ANIMNUMFRAMES but using same ANIMTIMEOUTFREQ results in smoother & slower (resp. coarser & faster) animation


AUTOPILOTTHRESHOLD = 0.95*TURNLIMITCOUNT # if AUTO is selected, Autopilot will move when the Timer's *abstract* counter is at or below this number (higher <=> sooner), must be positive!


IMGHEIGHT = 2*2*MATRIXRADIUSPOSRANGE*MATRIXRADIUSWEIGHT*MATRIXENTRYRANGE # seems to be a "comfortable" height
IMGWIDTH = IMGHEIGHT+(2*MATRIXENTRYRANGE) # seems to be a "comfortable" width (only difference between width and height is that center can be plus/minus MATRIXENTRYRANGE from origin, hence add double that)
IMGAXISTHICKNESS = 1
IMGCENTERDOTRADIUS = 0.25 # thickness of dot (= radius of tiny subdisc) used to indicate discs' centers during Adrenaline
IMGMAGNIFY = 7.5 # previous (e.g. MATRIXENTRYRANGE, MATRIXRADIUSWEIGHT,IMGHEIGHT, IMGWIDTH) are relative measurements, this controls absolute size
IMGAXISCOLOR = ImageColor.getrgb( "Black" )
IMGPLANECOLOR = ImageColor.getrgb( "MistyRose" )
IMGMYCOLOR = ImageColor.getrgb( "LimeGreen" )
IMGOPPCOLOR = ImageColor.getrgb( "DarkViolet" )
IMGOUTLINECOLOR = ImageColor.getrgb( "Black" )
IMGDISTINGUISHCOLOR = ImageColor.getrgb( "GreenYellow" )
IMGMYADRENALINECOLOR = ImageColor.getrgb( "DarkGreen" )
IMGOPPADRENALINECOLOR = ImageColor.getrgb( "Indigo" )

