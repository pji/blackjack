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
The following features are possible for future versions:

* Separate number of seats from number of players.
	* Fix game.Engine.seats when restoring from file.
	* Allow empty seats.
	* Allow players to join partway through a hand.
* Allow player interaction.
	* Display recent actions in TableUI.
	* Allow players to notice other players.
	* Allow players to react to other players.
	* Allow players to notice actions of other players.
	* Allow players to react to the actions of other players.
	* Allow casino to react to players.
	* Add casino catching and removing card counting players.
	* Allow players to join a table partway through the shoe.
* Build UI for saving and restoring game state.
* Allow splitting more than once.
* Add ability to configure by file.
* Allow multiple human players to play in single game over network.
* Add "How-To" to help.
* Add "How-To" to Table interface.


Testing
-------
To run the unit tests, pull the repository and run the following from 
the root of the repository::

    python3 -m unittest discover tests

