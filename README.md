# Battle-City-Project
A tank battle game based on _"Battle City"_ (Namco, 1985) using [Pyxel](https://github.com/kitao/pyxel) and [Pxyelgrid](https://github.com/UPD-CS12-232/pyxelgrid).

Made by Aeron Dann Peñaflorida and Alessandra Mae Gomez for CS12 MP1.
## How to Run

Install Python and [Pyxel](https://github.com/kitao/pyxel?tab=readme-ov-file#how-to-install) if you haven't already.

Go to CMD and run the following command to install pyxelgrid
```
pip3 install --upgrade git+https://github.com/UPD-CS12-232/pyxelgrid 
```
Go to the main directory of the game and run the following command:  
``` 
python mp1final.py
```

## Game Controls:
W,A,S,D - Movement keys
Space Bar - Shoot Bullet
1 - Restart the Game(start from stage 1)
2-  Revive Tank(if lives!=0)
PAM- CheatCode(wins the stage)

## Powerup Mechanics:
If the player killed at least half of the enemies, a random(question mark) cell will 
spawn in a cell with no state.
If the player went on the question mark cell, the player will randomly get either a speedboost, an extra life, 
or there will be no delay in turning the tank (the tank has a cooldown in changing direction) for a short period of time.

## Stage Format:
The Dataclass of Tanks,Bullets,Cells, and Stage are in the stage file.
The stage file contains a class called Stages, which contains the code for the stages and is stored in a list

Highest Phase Achieved- Phase 3

## Contributions:
Aeron Dann Penaflorida-Programming,Format of Stage File, Code Documentation
Alessandra Mae Gomez- Creation of Maps and Design,Video Demo
