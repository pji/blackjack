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


The Rules
---------
The blackjack rules used for a default game of blackjack come from
`Blackjack—Card Game Rules`_ by Bicycle Cards.

.. _`Blackjack—Card Game Rules`: https://bicyclecards.com/how-to-play/blackjack/


Recent Updates
--------------
The following was changed in v0.1.1:

*   Switched from `pipenv` to `poetry`.
*   Moved source into `src` directory.
*   Improved documentation.
*   Typing clean up.


Still To Do
-----------
The following features are possible for future versions:

* Build UI for saving and restoring game state.

    *   Create menu interface.
    *   Select item in menu.
    *   Escape to menu.
    
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
	
* Add optional rules.

    * Allow splitting more than once.
    * Allow resplitting aces.
    * Allow early surrender.
    * Allow dealer hitting soft 17.
    * Allow 6:5 payout on player blackjack.
    * Allow doubling only on hard totals of 9, 10, or 11.
    * Allow side bets.
    * Add late surrender.
    * Add doubling after split.
    
* Add ability to configure by file.
* Allow multiple human players to play in single game over network.


Testing
-------
To run the unit tests, pull the repository and run the following from 
the root of the repository::

    python -m pytest tests/

