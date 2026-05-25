# brick-blasters
A game based on the arcade classic Breakout which is simple but fun.
The sideswipe mode is where you catch the ball cleanly on either side of the paddle. This will lock the ball inside the paddle frame, allowing you to carry it left and right as long as you move the paddle with the ball. (*Showcased in the video*) Be careful though. The ball has a chance of launching itself under the paddle and falling into its demise while using this!
https://github.com/user-attachments/assets/f486664b-9508-4d9e-ac8f-541810387cf3
The angle and direction of the ball is also randomized every time you hit the paddle, also seen in the video.
Difficulties! Easy, Medium, Hard, and the HARDEST ONE YET, Holy difficulty! If you are ready for super-fast brick blasting action, give holy mode a try!
Gold bricks give you 2X score for 10 seconds. Nice, ain't it!
You can change the background song to any newgrounds song you want! Isn't that nice?
**YOU WILL NEED A FOLDER TO PUT THE EXECUTABLE IN FOR THE SCORE FILES TO STAY IN**

***COMPILE WITH PYGAME-CE INSTEAD OF PYGAME FOR THE BEST EXPERIENCE OF BRICK BLASTERS***

***V1.3 AND ABOVE INSTRUCTIONS***
How to compile: It's pretty simple, just pip install pygame-ce pygame-widgets cryptography pyinstaller and then run pyinstaller --noconfirm --onedir --windowed --icon="icon.png" --add-data "icon.png:." --add-data "hit-sound.mp3:." --add-data "WorkSans-Regular.ttf:." --add-data "background.mp3:." --add-data "break.mp3:." main.py on macos/linux and pyinstaller --noconfirm --onedir --windowed --icon="icon.png" --add-data "icon.png;." --add-data "hit-sound.mp3;." --add-data "WorkSans-Regular.ttf;." --add-data "background.mp3;." --add-data "break.mp3;." main.py on windows.

***V1.2 INSTRUCTIONS***
How to compile: It's pretty simple, just pip install pygame-ce cryptography pyinstaller and then run pyinstaller --noconsole --onefile --exclude-module=numpy --add-data "WorkSans-Regular.ttf:." main.py on macos/linux and pyinstaller --noconsole --onefile --exclude-module=numpy --add-data "WorkSans-Regular.ttf;." main.py on windows.

***V1.1 AND BELOW INSTRUCTIONS***
How to compile: It's pretty simple, just pip install pyinstaller and then run pyinstaller --noconsole --onefile --exclude-module=numpy --add-data "WorkSans-Regular.ttf:." main.py on macos/linux and pyinstaller --noconsole --onefile --exclude-module=numpy --add-data "WorkSans-Regular.ttf;." main.py on windows.

Enjoy the game!

