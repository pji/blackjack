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
* You don't know the suit or rank of a face down card.

Cards aren't directly exposed to user input, but it probably still 
makes sense for them to describe their data. That way, there is a 
chance to catch something weird that happens for easier debugging.

Based on those requirements, the following methods seem to make 
sense for the Card class:

* Card.flip()


Deck
~~~~
Next up is the deck the cards are drawn from. The characteristics of 
a blackjack deck are:

* The Deck class exists.
* An instance of the Deck class can be created.
* The Deck contains Card objects.
* The Deck can contain multiple complete standard decks of cards.
* The dealer can draw cards from the deck.
* Cards drawn from the deck are removed from the deck.
* The deck can be shuffled.
* Between 60 to 75 cards can be removed from the end of the deck to 
  make card counting harder.
* Cards are face down in the deck.

Based on those requirements, the following methods seems to make 
sense for the Deck class:

* Deck.build(num_decks)
* Deck.draw(num_cards)
* Deck.shuffle()
* Deck.random_cut(num_cards)

Deck.random_cut() is named random_cut() rather than cut() in case it 
it useful to have a method to more traditionally cut the deck in the 
future.


Hand
~~~~
Now I need an object to represent a hand in blackjack.

Do I, though? Could the hand just be a list stored as an attribute of 
the player? Maybe it doesn't need its own class. The answer depends on 
what a hand needs to be able to do. So, what does a hand need to have 
or do?

* A hand has cards.
* A hand has a score.
* A hand can be split into two hands.
* A hand can be hit.

Both list and object implementations will be able to hold cards and be 
hit, so that argues for list.

Does it make more sense for the hand to calculate it's own score and 
handle its own split or should this be handled by a function? Both of 
these are characteristic of blackjack hands, so there isn't really 
any reuse if I have them as separate functions. Though, the ace being 
worth either one or eleven depending on the situation does make it 
tricky.

Do you ever need to look at the dealer's hand in order to know whether 
to count an ace as one or eleven? Maybe, but that's more of a decision 
for the player not the hand. If scoring is done on the hand, then it 
probably makes sense to return all possible scores and allow the 
player to decide. It also only really matters for computer players 
other than the dealer, if those are ever implemented. The player can 
make the decision themselves when deciding whether to hit. And when 
the player's hand is compared to the dealer's hand, it will be 
obvious whether to count the aces as one or eleven.

After all of that, the score is something that is intrinsic to the 
hand, so it probably makes sense to go ahead and implement hands as 
a class, with the following custom methods:

* Hand.append()
* Hand.score()
* Hand.split()
* Hand.can_split()

One final thought, both decks and hands are collections of cards. Does 
it make sense to have a superclass for them that implements common 
methods like the MutableSequence protocol? That'll take quite a bit of 
refactoring, but it's probably worth it to be able to say hand[0] 
rather than hand.cards[0]. I'll go with Pile for the name of the 
superclass.