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

* Allow CLI to turn off the random cut when building the deck.
* Display recent actions in TableUI.
* Build UI for saving and restoring game state.
* Allow for insurance less than half of initial bet.
* Add optional card count to display.
* Allow variable bets.
* Allow players to notice other players.
* Allow players to react to other players.
* Allow players to notice actions of other players.
* Allow players to react to the actions of other players.
* Add card counting computer players.
* Add casino catching and removing card counting players.
* Allow splitting more than once.
* Add ability to configure by file.
* Add ability to configure at launch.
* Allow multiple human players to play in single game over network.


Testing
-------
To run the unit tests, pull the repository and run the following from 
the root of the repository::

    python3 -m unittest discover tests

