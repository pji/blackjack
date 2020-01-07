=========
blackjack
=========

Yet another Python implementation of blackjack. The main purpose of 
this is to play around with basic concepts.


To Run
------
If you clone the repository, you can run it. Right now, all that it 
does is show a game between automated players, but if you want to 
see that, you can.

To see a game that is only the dealer, run the following from the root 
of your local copy of the repository::

    python3 -m blackjack.cli -d

To see a game that is the dealer and one player::

    python3 -m blackjack.cli -1

To see a game that is the dealer and two players::

    python3 -m blackjack.cli -2


Still To Do
-----------
The following features are on the to-do list:

* Create more automated players with different behavior.
* Let the user control a player.
* Add UI that updates information in place rather than listing events.
* Create a kick-off script at root to ease starting the script


Testing
-------
To run the unit tests, pull the repository and run the following from 
the root of the repository::

    python3 -m unittest discover tests

