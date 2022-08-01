=========
blackjack
=========

Yet another Python implementation of blackjack. The main purpose of 
this is to play around with basic concepts.


To Run
------
To see a game that is only the dealer, run the following from the root 
of your local copy of the repository::

    python3 -m blackjack -d

To see a game that is the dealer and one player::

    python3 -m blackjack -1

To see a game that is the dealer and two players::

    python3 -m blackjack -2

If you want to play a game with a dealer and four random players::

    python3 -m blackjack -D

To construct a game with four computer players, you as the fifth 
player, the initial bet set to 100, and all players starting with 
100 chips::

    python3 -m blackjack -p 4 -u -c 100 -C 100


Still To Do
-----------
The primary to-do list is complete.

The following features are on the nice-to-have list:

* Write tests for CLI invocation.
* Allow CLI to restore game from save.
* Allow CLI to set name of save file.
* Allow multiple human players to play in single game over network.
* Build UI for saving and restoring game state.
* Allow for insurance less than half of initial bet.
* Add optional card count to display.
* Allow players to notice other players.
* Allow players to react to other players.
* Allow players to notice actions of other players.
* Allow players to react to the actions of other players.
* Add card counting computer players.
* Add casino catching and removing card counting players.
* Allow splitting more than once.
* Add ability to configure by file.
* Add ability to configure at launch.


Testing
-------
To run the unit tests, pull the repository and run the following from 
the root of the repository::

    python3 -m unittest discover tests

