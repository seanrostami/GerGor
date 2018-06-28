_last updated Jun 28, 2018_ 


_GerGor_ is a competitive two-player game inspired by the famous [Gershgorin Circle Theorem](https://en.wikipedia.org/wiki/Gershgorin_circle_theorem) from Linear Algebra. Each player has a collection of discs in a 2-dimensional plane; by quickly estimating sizes and positions of certain numbers in a matrix, and making an appropriate choice of entry, you transform your discs and try to capture your opponent's. 

![SAMPLE](https://github.com/seanrostami/GerGor/raw/master/EXAMPLE1.png "a typical view (EXAMPLE1.png)") 

GerGor is written in Python, executes correctly as-is in both version 2.X (for reasonably high X) and version 3.X of Python, and runs on Linux, Windows, and Mac. The GUI is created with [GTK+](https://en.wikipedia.org/wiki/GTK) and the charming graphics are created with the [Pillow](http://python-pillow.org/) fork of the classic _Python Imaging Library_ [PIL](https://en.wikipedia.org/wiki/Python_Imaging_Library) library. 


#### AUTHOR(S): ####

[Sean Rostami](https://www.linkedin.com/in/sean-rostami-77255a141/) 


#### CONTACT(S): ####

<sean.rostami@gmail.com> 


#### TABLE OF CONTENTS: ####

1) System Requirements 

2) Files 

3) How to Start the Game 

4) How to Play the Game (Rules) 

5) How the Program Operates 

6) Known Bugs 

7) Future Plans

8) Credits/Acknowledgements 

9) Testing 


#### SYSTEM REQUIREMENTS: ####

- Python, either v2 or v3 

- GTK+ for Python (more correctly, the PyGObject package) 

    _it is usually annoying to install PyGObject..._ 

- the Pillow package for Python, a continuation of the PIL library 

- playable on Linux, Windows, Mac if above requirements are satisfied 

    _see the bottom of this README for a list of actual tests_ 

- seems to require about 25 MB of RAM at all times 


#### FILES: ####

1) GERGOR.py		 (GUI, "main loop") 

2) GERGORCALLBACKS.py	 (GTK+ signal-handlers) 

3) GERGORCONFIG.py	 (configuration) 

4) gergorcomm.py	 (class) 

5) gergorimage.py	 (class) 

6) gergormatrix.py	 (classes) 

7) gergoranimation.py	 (class) 

8) gergorpaintable.py	 (class) 

9) GERGORICON.jpg	 (icon) 


#### HOW TO START THE GAME: ####

1) each player puts all of the above files into a single but arbitrary directory 

2) each player runs GERGOR.py from any working directory (the other .py files should be in the same directory) 

    _each user must have permission to create/read/write/delete a file in both working directories_ 

3) players communicate to each other their "connection info" (displayed at the top of each game window) 

4) players enter their opponent's connection info into the game (near the top of the game window) 

    _if both players are using the same computer, the only possibility at present, then connection info can be easily copied and pasted from one window to another_ 

5) each player presses CONNECT (near the top of the game window) 

    _see section "HOW THE PROGRAM OPERATES" below for an explanation of the seemingly oblique steps 3,4,5_ 

6) one player (random) starts, and the players alternate turns thereafter until one wins 


#### HOW TO PLAY THE GAME (RULES): ####

- Each player has a collection of discs in a 2-dimensional plane (yours are GREEN). You try to capture all the opponent's discs (PURPLE). For one disc to capture another means that the latter is completely contained within the former at the end of the former's turn (it is not sufficient for the latter to be contained in a union of two or more of the former). A player WINS if the other player has no discs. How to alter the positions and sizes of your discs is explained next. 

- Each player has a MATRIX, and the rows of their matrix define their discs in the following way: one special entry (the "focus" of that row, always indicated in BOLD) specifies the center of the disc, on the Horizontal Axis. The other entries contribute to the radius in a complicated way: see GerGorMatrix.get\_radius(...) if you are interested in the thorny details. In short, entries in a row nearer to the focus of that row (with wraparound!) are more significant than those farther, and only absolute value of an entry matters for calculation of the radius (the GUI reminds you of this via | | symbols). As a convenience, there is a SHOW button for each row of the matrix that will highlight the disc corresponding to that row. 

- You change the positions/sizes of your discs by clicking an entry in the matrix and ACCEPTing that choice: the focus of the row containing the entry you clicked becomes that entry, and the center/radius change accordingly (you can also UNDO your choice and make another, or PASS). Intuitively (and visually!), the disc corresponding to that row moves from its old center to its new center, and either grows or shrinks in size. At all times, no two rows of the matrix can have their focus contained in the same column -- if you choose as focus an entry in a column which already contains the focus of another row, that other row's focus exchanges with your selected row's previous focus. Because of this, even if the selected disc changes as intended, there can be unintended consequences involving that compensating disc. 

    _EXAMPLE: Consider the situation depicted in the photo above. The fourth active row (the eighth row overall) defines the small green disc D near the origin. Choosing and ACCEPTing the entry +43.8 in this row will cause two things to happen: D will move to a new center and change size, and the disc D' corresponding to the second active row (centered at -50.7 in the picture) will also move to a new center and change size. The new center for D will be +43.8, making it the rightmost green disc. It is difficult to say exactly what D's new radius will be, but it will be considerably bigger than the old radius: the entries nearest to the +43.8 entry are much bigger than those nearest to the +3.7 entry. The new center for D' will be -38.4 (fourth column), since it was displaced by D and D's original center was in the fourth colum. Quick visual inspection suggests that D's new radius will be slightly bigger than D's new radius._

- A player's usual goal is to quickly judge what selection will accomplish something worthwhile (there is a time-limit!). For example, you can estimate the centers/sizes of your opponent's discs by visually comparing them to your own discs, whose centers/sizes you know from knowledge of your own matrix (and the SHOW button). With such estimates, you can search your own matrix and more easily judge if there is a choice that will capture one or another of your opponent's discs. Although not the main purpose, I hope the game can be used to improve one's ability to perform quick numerical estimation and generally build mental sharpness. 

- At the end of any turn, if a player did not capture any discs, all that player's non-focus entries shrink slightly in absolute value. If a player captures at least one disc, all that player's non-focus entries grow slightly (once for each capture, with compounding, although no additional captures result from this a posteriori). In particular, the sizes (but not the centers) of all the player's discs change. 

- If a player has only one disc remaining at the start of a turn, there is a random chance that the disc will acquire "Adrenaline" for that turn. If a disc has Adrenaline (indicated by a DARK color), the rules for capture change: _For an Adrenalized disc to capture any other disc, the former need contain only the center of the latter_ (for convenience, the centers of discs are displayed to the players whenever Adrenaline is present). 

- To avoid convergence to highly static situations, a random uncaptured non-focus entry in the matrix changes sign at the end of each turn (note that this does not change the current discs' positions/sizes). 

- There is a non-human player called _Autopilot_, which can be activated or deactivated via the AUTO button. It is not very intelligent. 

- Virtually any aspect of the game other than its foundation can be easily changed in the file GERGORCONFIG.py: the various messages displayed to the players, how much time is allowed per turn, the colors appearing in the game, the granularity and speed of animations, the probability of Adrenaline, and so on. 


#### HOW THE PROGRAM OPERATES: ####

- Each player operates a completely independent instance of the game. Each process creates a temporary file (whose name involves a random integer) in its working directory from which it will receive information from the opponent. This independence is deliberate, so that the game might one day be extended to remote play with a minimum of changes. The two players connect to each other by communicating the location of their temporary files, which are conveniently displayed by the game and can be copied/pasted. In a future version of the game, the processes would connect to some server and the shared information would be a username or something. During Player A's turn, Player B's process has a function repeatedly checking its temporary file for data. When Player A completes the turn, the necessary data is written to Player B's temporary file, and the presence of data in that file causes Player A to initiate a new turn. Most of this is managed by the class **GerGorComm**. 

- All images are created using the Pillow library, a continuation of PIL, and images are displayed to the user by converting to a GdkPixbuf and loading into a GtkImage widget. Most of this is managed by the classes **GerGorImage** and **GerGorPaintable**. Animations are simply rapidly displayed sequences of such images. Most of the construction of such sequences is managed by the class **GerGorAnimation**. 

- The numerical/logical data of the MATRIX itself is managed by the class **GerGorMatrix**, which itself delegates certain responsibilities to the classes **GerGorMatrixRow** and **GerGorMatrixEntry**. 

- The script **GERGOR**.py creates the GUI and specifies handlers to respond to player input, and the handlers themselves are defined in file **GERGORCALLBACKS**.py. The most complex file is GERGORCALLBACKS. As discussed already, most gameplay parameters are contained in **GERGORCONFIG**.py. 

- The issues required to get simultaneous v2 and v3 compatibility were mostly related to Lists, especially implications of the fact that filter(...) in v3 returns a single-use iterable rather than a List, but also the lack of convenient methods like .copy() and .clear(). It was also important that boolean contexts in v2 trigger classes' .\_\_nonzero\_\_ and ignore their .\_\_bool\_\_. Finally, 'bytes' objects are used in gergorimage.py but, evidently, the differences between v2 and v3 here are hidden by the GLib.Bytes constructor into which they are fed. 

- There are no sounds. 

- In certain places I used the following encapsulation principle that has been very helpful to me and is related to the "double dual" from Linear Algebra: If class X has a method F that is to operate on the data D in a class Y, one should define a method .callF(\_) for Y that performs \_.F(Y.D) and accomplish the task via Y.callF(X). 


#### KNOWN BUGS: ####

- On Macs, it seems like the game suspends/hibernates if the window is minimized for more than a few seconds. For example, if your opponent is Autopilot and minimized, you will wait indefinitely for your next turn. If you unminimize it, everything continues from what is presumably time of the suspension. Probably there is a way for each process to announce "I'm doing stuff! Don't freeze me!" to the OS. 

- Is it unsafe to set GERGORICON.jpg as the GtkWindow's "official" icon, without checking its bonafides first? 

- The "sad face" is too small on Windows...


#### FUTURE PLANS: ####

- make images dynamically resizable (GtkWidget's screen-changed signal, modify IMGMAGNIFY) 

- revisit constants in GERGORCONFIG.py, and gameplay in general 

- improve the strategy of Autopilot (but not too much!) 

- change communication from plaintext to raw binary? 

- allow players to use different computers and communicate via internet (AWS server?) 

- do we want hotkeys? 

- add sounds? 

- make the buttons of the matrix square? 

- allow more than two players in one game? (via Hans Chaumont)


#### CREDITS/ACKNOWLEDGEMENTS: ####

- The basic idea for this game comes from the Gershgorin Circle Theorem in Linear Algebra. More precisely, the idea came from the question of how the Gershgorin Region changes when the rows of the matrix are permuted (exchanging rows i and j is equivalent to choosing i's new focus to be j's current focus). Sadly, calculating radii exactly as the theorem specifies does not produce a dynamic game, so the details were modified. 

- This program, including the GUI, was written using only [gedit](https://en.wikipedia.org/wiki/Gedit). 

- I learned that PIL.Image could be painlessly converted to GdkPixbuf from gist.github.com/mozbugbox's "pixbuf2pillow" module. However, a modification was necessary -- see remarks in gergorimage.py. I warmly thank Christopher Reiter of gitlab.gnome.org/GNOME/pygobject for helping me to understand the issues surrounding GdkPixbuf's .new\_from\_data(...) and .new\_from\_bytes(...) methods. 

- Many thanks to Hans Chaumont for playing/testing and for several worthwhile suggestions.


#### ACTUALLY TESTED ON: ####

- Ubuntu 16.04 LTS (custom desktop), 4.4.0-128-generic, #154-Ubuntu SMP; Python 3.5.2, pygobject 3.20.0, Pillow 5.1.0 

- Ubuntu 16.04 LTS (custom desktop), 4.4.0-128-generic, #154-Ubuntu SMP; Python 2.7.12, pygobject 3.20.0, Pillow 5.1.0 

- Windows 10 Home (custom desktop), version 1709; Python 2.7.15, PyGObject 3.24.1, Pillow 5.1.0 

    _PyGObject for Windows installed from sourceforge.net/projects/pygobjectwin32_

- old Windows 7 (Dell netbook); Python 2.7.15, PyGObject 3.24.1, Pillow 5.1.0 

    _PyGObject for Windows installed from sourceforge.net/projects/pygobjectwin32_

- OS X 10.11.6 (MacBook Pro), Darwin 15.6.0; Python 3.6.5, PyGObject 3.28.3, Pillow 5.0.0 

- OS X 10.11.6 (MacBook Pro), Darwin 15.6.0; Python 2.7.15, PyGObject 3.28.3, Pillow 5.0.0

    _at this time, there seem to be issues with Pillow 5.1 on Macs so I demoted it to 5.0.0..._

- MacOS 10.12.6 (Macbook Air), Darwin ???; Python 3.5.2, PyGObject 3.28.3, Pillow 3.2.0 
