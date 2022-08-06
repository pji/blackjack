=========
blackjack
=========

Yet another Python implementation of blackjack. The main purpose of 
this is to play around with basic concepts.


To Run
------
To run a basic game, run the following from the root of your local copy
of the repository::

    python3 -m blackjack


Still To Do
-----------
The primary to-do list is complete.

The following features are on the nice-to-have list:

* Allow user variable bets.
    * Create willbet.py that governs player betting.
    * Create number input prompt.
    * Add input prompt to game.start.
* Allow computer player variable bets.
* Fix game.Engine.seats when restoring from file.
* Allow players to count cards.
* Allow players to be bad at counting cards.
* Allow users to join a table partway through the shoe.
* Display recent actions in TableUI.
* Build UI for saving and restoring game state.
* Allow for insurance less than half of initial bet.
* Allow players to notice other players.
* Allow players to react to other players.
* Allow players to notice actions of other players.
* Allow players to react to the actions of other players.
* Allow casino to react to players.
* Add casino catching and removing card counting players.
* Allow splitting more than once.
* Add ability to configure by file.
* Allow multiple human players to play in single game over network.


Testing
-------
To run the unit tests, pull the repository and run the following from 
the root of the repository::

    python3 -m unittest discover tests

