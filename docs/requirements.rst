===============================
blackjack Requirements Document
===============================

The purpose of this document is to detail the requirements for the 
blackjack game. This is an initial take to help with planning. There 
may be additional requirements or non-required features added in the 
future.


Purpose
-------
The purposes of the blackjack game are:

* To be able to run a basic blackjack game from the CLI.
* To solidify my understanding of basic OOP concepts in Python.


Functional Requirements
-----------------------
The following are the functional requirements for blackjack:

1. blackjack has two players: a human player and a computer dealer
2. blackjack can construct and shuffle a common 6-deck deck
3. blackjack can take an initial bet from the player
4. blackjack can deal the hands for the round
5. blackjack can allow the player to hit
6. blackjack can allow the player to split
7. blackjack can correctly score the hand
8. blackjack can run the dealer player
9. blackjack can determine the winner
10. blackjack can pay out on the bet
11. blackjack can track the player's chips between games


Technical Requirements
----------------------
The following are the technical requirements for blackjack:

1. blackjack is written in Python
2. blackjack will have a command line interface


Design Discussion
-----------------
This thing has a lot of moving pieces. It's probably good to start 
breaking down pieces I'm going to need:

* Players
* Cards
* A deck of cards
* Hands of cards


Cards
~~~~~
The cards are the core piece here, so it probably makes sense to start 
with them. What characteristics do cards in blackjack have:

* Suit
* Rank
* Value, which varies for aces
* Facing

I think that translates into the following requirements:

* The Card class exists.
* An instance of the Card class can be created.
* A Card object has a suit.
* A Card object has a rank.
* A Card object has a value.
* A Card object that is an ace can have a value of either 1 or 11.
* A Card object has a facing.
* A Card object's facing can be flipped.

Cards aren't directly exposed to user input, but it probably still 
makes sense for them to describe their data. That way, there is a 
chance to catch something weird that happens for easier debugging.