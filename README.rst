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


Still To Do
-----------
The following features are planned for the 0.1.0 release:

*   x Allow running as a console script.
*   x Handle the additional bet when splitting the hand.
    *   x Only allow splitting when player has chips for the bet.
    *   x Take the chips for the bet from the player.
*   x End round immediately if dealer has natural blackjack.
    *   x Dealer checks if face-up card is a 10, J, Q, K, or A.
    *   x If dealer has a natural, skip to settlement.
    *   x If player has a natural, they get their bet back.
    *   x All other players lose.
*   x Add opening splash screen.
    *   x Display splash screen.
    *   x Clear splash screen from TableUI before play begins.

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
* Build UI for saving and restoring game state.
* Add ability to configure by file.
* Allow multiple human players to play in single game over network.
* Add "How-To" to help.
* Add "How-To" to Table interface.


Testing
-------
To run the unit tests, pull the repository and run the following from 
the root of the repository::

    python3 -m unittest discover tests

