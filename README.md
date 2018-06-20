# GerGor
GerGor is a competitive two-player game inspired by the famous "Gershgorin Circle Theorem" (en.wikipedia.org/wiki/Gershgorin_circle_theorem) from Linear Algebra. Each player has a collection of discs in a 2-dimensional plane; by quickly estimating sizes and positions of certain numbers in a matrix, and making an appropriate choice of entry, you transform your discs and try to capture your opponent's. This prototype is written in Python, executes correctly as-is in both version 2.X (for reasonably high X) and version 3.X of Python, and runs on Linux, Windows, and Mac. The GUI is created with GTK+ (en.wikipedia.org/wiki/GTK+) and the charming graphics are created with the Pillow fork of the classic PIL library (en.wikipedia.org/wiki/Python_Imaging_Library).

AUTHOR(S):
Sean Rostami


CONTACT(S):
sean.rostami@gmail.com


SYSTEM REQUIREMENTS:
1) Python, either v2 or v3
2) GTK+ for Python (more correctly, the PyGObject* package)
3) the Pillow package for Python, a continuation of the classic PIL library
4) playable** on Linux, Windows, Mac if above requirements are satisfied
5) seems to require about 25 MB of RAM at all times
* it is usually annoying to install PyGObject...
** see the bottom of this README for a list of actual tests


FILES:
1) GERGOR.py		(GUI, "main loop")
2) gergoranimation.py	(class)
3) GERGORCALLBACKS.py	(GTK+ signal-handlers)
4) gergorcomm.py	(class)
5) GERGORCONFIG.py	(configuration)
6) GERGORICON.jpg	(icon)
7) gergorimage.py	(class)
8) gergormatrix.py	(classes)
9) gergorpaintable.py	(class)


HOW TO START GAME:
1) each player puts all of the above files into a single but arbitrary directory
2) each player runs GERGOR.py from any* working directory (the other .py files should be in the same directory)
3) players communicate** to each other their "connection info" (displayed at the top of each game window)
4) players enter** their opponent's connection info into the game (near the top of the game window)
5) each player presses CONNECT (near the top of the game window)
6) one player (random) starts, and the players alternate turns thereafter until one wins
* each user must have permission to create/read/write/delete a file in both working directories
** if both players are using the same computer, the only possibility at present, then connection info can be easily copied and pasted from one window to another
(see section "HOW THE PROGRAM OPERATES" below for an explanation of the possibly puzzling steps 3,4,5)


RULES OF THE GAME: 
- Each player has a collection of discs in a 2-dimensional plane (yours are GREEN). You try to capture all the opponent's discs (PURPLE). For one disc to capture another means that the latter is completely contained within the former at the end of the former's turn (it is not sufficient for the latter to be contained in a union of two or more of the former). A player WINS if the other player has no discs. 
- Each player has a MATRIX, and the rows of their matrix define their discs in the following way: one special entry (the "focus" of that row, always indicated in BOLD) specifies the center of the disc, on the Horizontal Axis, and the other entries contribute to the radius in a complicated way (see GerGorMatrix.get_radius for details). Entries in a row nearer to the focus of that row are more significant than those farther. For calculation of the radius, the sign is ignored and only the absolute value of the entry matters (the GUI reminds you of this via | | symbols). As a convenience, there is a SHOW button for each row of the matrix that will highlight the disc corresponding to that row.
- You change the positions/sizes of your discs by clicking an entry in the matrix: the focus of the row containing the entry you clicked becomes that entry, and the center/radius change accordingly (you can also PASS, changing nothing). Intuitively (and visually!), the disc corresponding to that row moves from its old center to its new center, and either grows or shrinks in size. At all times, no two rows of the matrix can have their focus contained in the same column -- if you choose as focus an entry in a column which already contains the focus of another row, that other row's focus exchanges with your selected row's previous focus. Because of this, even if the selected disc changes as intended, there can be unintended consequences involving that compensating disc. 
- A player's usual goal is to quickly judge what selection will accomplish something worthwhile (there is a time-limit!). For example, you can estimate the centers/sizes of your opponent's discs by visually comparing them to your own discs, whose centers/sizes you know from knowledge of your own matrix (and the SHOW button). You can then plan to capture one or another of them by searching for searching in your matrix for a suitable entry with sufficiently large neighbors. Although not the purpose of the game, I suspect the game can be used to improve one's ability to perform quick numerical estimation and generally build mental sharpness.
- At the end of any turn, if a player did not capture any discs, all that player's non-focus entries shrink slightly in absolute value. If a player captures at least one disc, all that player's non-focus entries grow slightly (once for each capture, with compounding, although no additional captures result from this after the fact). In particular, the sizes (but not the centers) of all the player's discs change. 
- If a player has only one disc remaining at the start of a turn, there is a random chance that the disc will acquire "Adrenaline" for that turn. If a disc has Adrenaline, the rules for capture change: for an Adrenalized disc to capture any other disc. the former must contain only the center of the latter (for convenience, the centers of discs are displayed to the players whenever Adrenaline is present). 
- To avoid convergence to highly static situations, a random non-focus uncaptured entry in the matrix changes sign at the end of each turn (note that this does not change the current discs' positions/sizes). 
- There is a non-human player called Autopilot, which can be activated or deactivated via the AUTO button. It is not very intelligent. 
- The current "phase" of the game is printed at the bottom of the game's window. 
- Virtually any aspect of the game other than its foundation can be easily changed in the file GERGORCONFIG.py: the various messages displayed to the players, how much time the TIMER allows, the colors appearing in the game, the granularity and speed of animations, the probability of Adrenaline, and many other things.


HOW THE PROGRAM OPERATES:
- Each player operates a completely independent instance of the game. Each process creates a temporary file in its working directory from which it will receive information from the opponent. This independence is deliberate, so that the game might one day be extended to remote play with a minimum of changes. The two players connect to each other by communicating the location of their temporary files, which are conveniently displayed by the game and can be copied/pasted. In a future version of the game, the processes would connect to some server and the shared information would be a username or something. During Player A's turn, Player B's process has a function repeatedly checking its temporary file for data. When Player A completes the turn, the necessary data is written to Player B's temporary file, and the presence of data in that file causes Player A to initiate a new turn. Most of this is managed by the class GerGorComm.
- All images are created using the Pillow library, a continuation of the "Python Imaging Library" PIL, and images are displayed to the user by converting to a GdkPixbuf and loading into a GtkImage widget. Most of this is managed by the classes GerGorImage and GerGorPaintable.
- Animations are simply rapidly displayed sequences of such images. Most of this is managed by the class GerGorAnimation.
- There are no sounds. 
- The numerical/logical data of the MATRIX itself is managed by the class GerGorMatrix, which itself delegates certain responsibilities to the classes GerGorMatrixRow and GerGorMatrixEntry. 
- I attempted to use as much as possible the following encapsulation principle that I quite like and is related to the "double dual" from Linear Algebra: If class X has a method F that is to operate on the data D in a class Y, one should define a method .callF(_) for Y that performs _.F(Y.D) and accomplish the task via Y.callF(X).
- The issues required to get simultaneous v2 and v3 compatibility were mostly related to Lists, especially implications of the fact that filter(_,_) in v3 returns a single-use iterable rather than a List, but also the lack of convenient methods like .copy() and .clear(). It was also important that boolean contexts in v2 trigger classes' .__nonzero__ and ignore .__bool__. Finally, 'bytes' objects are used in gergorimage.py but, evidently, the differences between v2 and v3 here are hidden by the GLib.Bytes constructor into which they are fed.


KNOWN BUGS:
1) On Macs, it seems like the game suspends/hibernates if the window is minimized for more than a few seconds. For example, if your opponent is Autopilot and minimized, you will wait indefinitely for your next turn. If you unminimize it, everything continues from what is presumably time of the suspension. Probably there is a way for each process to announce "I'm doing stuff! Don't freeze me!" to the OS.
2) Is it unsafe to set GERGORICON.jpg as the GtkWindow's "official" icon, without checking its bonafides first?
3) The "sad face" is too small on Windows...


FOR THE FUTURE:
1) make images dynamically resizable (connect to GtkWidget's screen-changed signal, get new dimensions, modify IMGMAGNIFY accordingly)
2) revisit constants in GERGORCONFIG.py, and gameplay in general
3) improve the strategy of the Autopilot (but not too much!)
4) do we want hotkeys?
5) allow players to use different computers and communicate via internet
6) add sounds?
7) make the buttons of the matrix square?


CREDITS/ACKNOWLEDGEMENTS:
- The basic idea for this game comes from the Gershgorin Circle Theorem (en.wikipedia.org/wiki/Gershgorin_circle_theorem) in Linear Algebra. More precisely, the idea came from the question of how the Gershgorin Region changes when the rows of the matrix are permuted. Sadly, calculating radii exactly as the theorem specifies does not produce a dynamic game, so the details were modified. 
- I learned that PIL.Image could be painlessly converted to GdkPixbuf from gist.github.com/mozbugbox's "pixbuf2pillow" module. However, a modification was necessary -- see remarks in gergorimage.py. I warmly thank Christopher Reiter of gitlab.gnome.org/GNOME/pygobject for helping me to understand the issues surrounding .new_from_data and .new_from_bytes -- see remarks in gergorimage.py.
- This program, including the GUI, was written using only gedit.


ACTUALLY TESTED ON:
- Ubuntu 16.04 LTS, 4.4.0-128-generic, #154-Ubuntu SMP; Python 3.5.2, pygobject 3.20.0, Pillow 5.1.0
- Ubuntu 16.04 LTS, 4.4.0-128-generic, #154-Ubuntu SMP; Python 2.7.12, pygobject 3.20.0, Pillow 5.1.0
- Windows 10 Home, version 1709; Python 2.7.15, PyGObject* 3.24.1, Pillow 5.1.0
- old Windows 7; Python 2.7.15, PyGObject* 3.24.1, Pillow 5.1.0
- OS X 10.11.6 (MacBook Pro), Darwin 15.6.0; Python 3.6.5, PyGObject 3.28.3, Pillow 5.0.0**
- OS X 10.11.6 (MacBook Pro), Darwin 15.6.0; Python 2.7.15, PyGObject 3.28.3, Pillow 5.0.0**
* sourceforge.net/projects/pygobjectwin32
** at this time, there seem to be issues with Pillow 5.1 on Macs...
