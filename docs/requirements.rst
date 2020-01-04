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


Player
------
I may add more later, but initially there are two players, the dealer 
and the end user. The dealer is computer driven, and the end user is 
driven by the end user. What do the two have in common?

* They are playing blackjack.
* They have at least one hand of cards.
* They can hit.
* They can stand.
* They can win or lose.
* They have some process to determine their actions.

That's not a lot in common, but I think there is enough for an 
abstract base class there. I'll call it Player, and the following 
attribute probably make sense:

* Player.hands

I could split the dealer out, leaving the creation of a base class for 
players to whenever I implement other computer players. They will have 
more in common with the human player since they will have to decide on 
betting and splitting. But something is telling me keeping this more 
organized from the start will make this easier, so I'll go ahead and 
keep the dealer in.

Since players are a different thing from cards, I'll put them in their 
own module.


Dealer and Pattern of Play
--------------------------
Players probably shouldn't be designed in a vacuum. They are going to 
be interacting with the core game loop. So, the methods needed probably 
stem from that. So, I'm going to step back and think about the core 
game loop, but a simpler version. What if this was a solitaire game 
with only the dealer following the dealer's rules to get as close to 
21 as possible.

The following events happen:

* The dealer deals their first card.
* The dealer deals their second card.
* The dealer performs the hit loop:
    * The dealer decides whether to hit.
    * If yes, get the card and go to top of the loop.
    * If no, exit the loop.
* Final score is determined.
* The round ends.

Terminology is a little awkward here since the Dealer isn't actually 
dealing the cards, the game loop is (though, that can be changed if we 
want the Dealer to be able to cheat in the future), but those are the 
events that need to be accounted for.

Here's a question: should the game loop know when to deal cards, or 
should the players request cards? I'm going to start with having the 
game loop know that, but I can change it in the future if needed.

The game loop itself is going to be a function that is running from a 
module named game.


Dealing a Card to a Hand
------------------------
This is the process for dealing a card to a player:

1. The game gets the next player.
2. The game gets the player's next hand.
3. The game gives a card to that hand.
4. The game determines if the player has another hand.
    a. If yes, then go to 2.
    b. If no, then go to 1.

This means the player needs to:

*   Tell the game whether it has more hands.
*   Give the game a hand.

And the hand must:

*   Accept a new card.

Hand.cards isn't a tuple yet, but it probably will need to be when 
saving games is implemented. You can't really trust the contents of 
lists since they are mutable and can be directly accessed. So, it's 
a bit overkill to implement methods for these, but it will save time 
when descriptors are implemented on Hand and Player.

That said, the two things that the player has to do are accomplished 
by passing the game an iterator on Player.hands. Since Player.hands is 
a list or a tuple, then it is already iterible. No need to add a 
method there.

So, the end result of this is that Hand needs a append() method, which 
it already has.


Hitting
-------
The player needs to communicate to the game loop whether or not they 
want to hit or stand. This probably works like this:

1. The game gets the next player.
2. The game gets the player's next hand.
3. The game asks the player if they want to hit or stand.
    a. If hit:
        i. The game gives the card to the hand.
        ii. Return to 3
    b. If stand, continue
4. The game determines if the player has another hand.
    a. If yes, go to 2
    b. If no, go to 1

The logic inside the dealer to determine whether to hit would be 
something like this:

1. Get current possible scores of hand. (This means player needs to 
   know which had the game is looking at.)
2. Determine the highest score that is <= to 21
    a. If no such score exists, the hand has busted, so stand and go to 4
    b. Otherwise, this is the score
3. Determine whether to hit:
    a. If the score is >= 17, stand
    b. Otherwise, hit
4. Return the stand or hit

This is all great, but... the UI needs to be updated with each hit.


UI
--
I'm starting, and honestly probably ending, with a CLI because I'm old 
and it reminds me of when I was young. I'll try to avoid baking that 
into the functioning of the game, so I can switch to a GUI of some 
kind if I ever feel like it. But, for now, CLI it is.

So, curses would be the obvious solution here, but it's apparently 
Unix only. No point in editorializing about that here, but it does 
make me hesitant to use it. For the moment I'll just stick to fairly 
standard text output. For this initial take, let's do something like:: 

    Dealer was dealt 7♣ ──.
    Dealer flips their second card to reveal 7♣ 9♥.
    Dealer hits, getting 5♦.
    Dealer stands with 7♣ 9♥ 5♦.
    Play again? (Y/n)
    >

There are probably two ways to accomplish this without making game 
have to know things about the UI:

* game's functions exit after each draw.
* game's functions are coroutines that get called by the UI.

There is probably some way to do it with the first bullet, but it 
seems more awkward. When I have more than one player, I'd have to 
have some way of keeping track of where I am in the deal or play 
process, which the coroutine can handle on its own.


Subclassing Player
------------------
Is a dealer a subclass of Player, or is it just Player that gets a 
specific function for will_hit() passed in? Though, the dealer is 
probably a bad example case for this, since dealers don't have to bet. 

Is an agressive player versus a conservative player difference 
subclasses of Player, or are they just players with different 
will_hit() methods patched in? Well, on one had, I'm probably 
only ever creating one instance of those subclasses at a time if 
I make them subclasses, which seems like a waste. On the other 
hand, I've not seen a pattern for monkey-patching instances that 
is similar to the factory pattern. So, I should go with the factory 
pattern, probably.


Making Decisions
----------------
I'm going to have computer players, and I want to have some ability 
for them to act both rationally and irrationally. The more information 
these computer players have, the more things they can base their 
decisions on. But, the more information that the computer players 
have, the more information is going to have to be moved around by the 
game.

The current issue is this: what information does a Player need to make 
the will_split decision? This boils down to the question:

    Does the player think that paying the extra $BET to split the hand 
    will improve their chances to meet their goal (likely to win)?

Here is information that is definitely relevant:

*   The player's hand
*   The dealer's hand
*   The cost of the $BET
*   The amount of money the player has left
*   The cards that have been seen since the last shuffle

It's that last one that is the trickiest. 

It tells you how likely you 
are to draw a card that you need. If you are likely to get the cards 
you need and the dealer isn't, then the split is likely a better idea 
than if you are less likely to get the cards you need than the dealer 
is. So, to get computer-perfect play, it's important.

But, it's, basically, all the information in the game. That's a lot 
to be tracking through the various functions and methods involved. 
Right now, I don't even have a way to record what happened with 
previous games, so I'd need to implement that plus pass in every 
visible hand just to send to the split() function.

Maybe this is where game needs to be an object rather than a series 
of functions. That would allow the game state to be saved as 
attributes that a split() method could access if needed, but ignore 
otherwise. I was trying not to complicate the game by making it a 
class, but it seems like there are definite benefits to doing so.

And, heck, if I'm making it a class anyway, I might as well make it 
a context manager.

OK, that wasn't where I was expecting this to go, but it does simplify 
the signature of split() quite a bit. The signature of will_split is 
probably still fairly complicated, though.