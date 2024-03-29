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
is similar to the class factory pattern. So, I should go with the 
class factory pattern, probably.


Making Decisions: will_split
----------------------------
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


Betting
-------
It wouldn't be blackjack without betting. With regards to betting the 
following will be needed:

* Give each player a number of chips.
* Track the player's chips.
* Get a decision from the player whether to buy in.
* Set the buy-in for the game.
* Subtract the buy-in from each player's chip total.
* Subtract the extra bet on a split.
* Pay out when the player wins.
* Pay out x1.5 when the player wins with a blackjack.
* Pay out normally when the player wins with a 21 on split aces.
* Allow the player to double down on a starting total of 9, 10, or 11. 
* Allow the player to buy insurance on a dealer with an ace showing.
* Pay out insurance if the dealer has a blackjack.

Should subtracting the buy-in be part of Game.deal() or should there 
be a new phase, which is something like Game.buyin()? Doing it in 
deal() would tie the betting to getting the cards directly. However, 
I think I'm going to want a phase where computer players without chips 
can bow out and maybe be replaced. Since buying-in would be the last 
step of that proces, I think having this separate buy-in/wallet 
checking phase is useful. I'll call it buyin() for now, but maybe 
their are better names I can come up with in the future.


Making Decisions Revisited
--------------------------
Let's list out all the decisions a player needs to make:

* Whether to buy into the round.
* Whether to hit or stand.
* Whether to split.
* Whether to double down.
* Whether to insure.

So, as Player is designed right now, that's five different methods:

* will_buyin
* will_hit
* will_split
* will_double_down
* will_insure

I think keeping them a methods still works. That is a lot of them, 
though, for my playerfactory(). Maybe I need to review the purpose 
of the Factory pattern to make sure I'm not misusing it. That said, 
I do want to be able to randomly mix strategies in computer players, 
and having a playerfactory() seems like the best way to do that.

Some research later....

The factories I'm creating are class factories, which I picked up from 
*Fluent Python.* The general factory pattern, though, is an object 
factory. I can't really find a lot on when to use a class factory 
versus manually defining the classes. Given I eventually want to 
implement randomizing which of the strategies a computer player can 
have, I think it makes sence to continue to use the class factory, 
even though it is probably way too complex for my needs at the 
moment.

Having five types of decision methods to pass into the factory does 
feel excessive, though. Thats just a lot of functions that are going 
to be sitting in players. Maybe I split those out into their own 
module? I'm not really sure that helps, though. Maybe instead of a 
class, players should have just been a dictionary, but then I 
couldn't have had descriptors to validate deserialization after a 
save is loaded. Enh. I'll keep going with this route, and we'll see 
where it goes.


Handling Input
--------------
Input cannot be trusted. So, if I'm going to be accepting input from 
the user, it needs to be validated. The validation design is to use 
trusted objects with data descriptors. So, how does this work with a 
simple case like getting input whether you want another game?

* Prompt for new game.
* Receive input as string from user. It should be a Y or N.
* UI.input() then places that string into the instantiation of a YesNo 
  object.
* The input is stored in the "value" attribute.
* The data descriptor validates the input and converts it to a bool.
* The YesNo object is then returned from UI.input().

YesNo is probably a common enough thing that it can live in model. But 
ones that hold information specific to a different module, should live 
in that module.

Is this overkill? Maybe. I could just handle the validation in the 
method that's handling the input rather than creating a class. But, 
data descriptors are the validation pattern, and I'd rather not have 
multiple ways I'm doing validation. So, potential overkill it is, 
then.


Dynamic UI
----------
The goal of the DynamicUI is to present the game like a table that 
gets updated rather than a scrolling log of events. In order to do 
that, the UI needs to keep track of the players in the game. That's 
probably best handled by an event coming from the game. That way I 
can enable new players in the middle of a game in the future.

I think how this is going to need to work without curses is that the 
UI object will need to track each player's row. And since we need to 
know what to delete in order to refresh the screen, I'll probably 
have to store the previous message displayed somewhere, too.

What should the interface look like? Maybe something like this:

    Player  Hand        Bet Chips   Status
    --------------------------------------
    Dealer  7c --       --  --      Receives hand.
    John    Js 10h      20  192.0   Stands.
    Michael Qd 2d Ks    20   89.5   Stands.
    You     5c 6h       20  205.5   Receives hand.
    --------------------------------------
    Double down? Y/n >

The status is a little tricky with the computer players going so 
quickly. Maybe put a little pause in there. We'll see.

Some time later....

Oh! Hey, guess what I just relearned. You can't backspace past a 
newline character. Since my plan for avoiding curses was to clear the 
table by using backspaces, I might be out of luck. Hm. Is there 
another way to do this?

I suppose this is where I have to break down and use my first third-
party module. Great. OK. But what should I use? There is, apparently, 
the windows-curses module that will allow curses to work on Windows 
systems, so maybe that's the answer. I develop using curses, and then 
add windows-curses as a requirement for Windows systems? I don't have 
any way to test that at the moment, though. I'll go ahead and give it 
a shot, though.

Some time later....

Using curses is going to be awkward. While it's not required, it wants 
to be run from inside a wrapper() function call, but since I want to 
be able to slot whatever UI I want into the game, I'd end up having to 
call the game differently when using the DynamicUI instead of just UI. 

Can this be resolved with a coroutine maybe? It doesn't seem like it. 
wrapper() wants a callable function. For a coroutine to work, it 
would need to already be running. There would be no way for me to call 
into that coroutine from the game object. The game object would have 
to be invoked from within the wrapper.

I could skip the wrapper and try to make this work, but I foresee many 
terminal restarts in that process. Maybe I just give up and go with a 
third-party library after all. I've looked briefly at three:

* blessings
* blessed
* asciimatics

blessings seems to be dead. The maintainer says he doesn't have the 
time to maintain it, and it's not been updated for Python 3.7, let 
alone Python 3.8. blessed seems better supported and is a fork of 
blessings, so that may be the way to go.  At least it supports Python 
3.7. The last option was asciimatics, which seems more active by 
doesn't list support for Python 3.7. asciimatics also says it's cross 
platform.

Maybe I'll try asciimatics on Python 3.7/3.8 and see if it works. I'm 
able to import it OK, but it needs a wrapper too. Hm. So how about 
blessed?

Some time later....

It works, but boy does it make debugging a pain.


The Splitting Problem
---------------------
Splitting involves the following actions:

* Determining that a split is possible
* Determining whether to make the split
* Splitting the hand
* Adding the additional bet for the second hand
* Determining if the split hands are aces
* If the split hands are aces, hit them once and stand
* Otherwise, handle each of the new hand's hits normally

How does that cause problems?

* It's both a hand update and a bet update to the UI
* The UI needs to make space for the extra hand

At the moment, DynamicUI doesn't keep any record of what is displayed 
in the UI. It doesn't need to because the location of the fields 
doesn't change. Since it doesn't change, it never needs to print the 
data out again.

But, the best UI for a split hand is probably to move all the players 
under the player who split down a row, and put the player-who-split's 
new hand in the now empty row. That that would require DynamicUI to:

* Keep track of the data in the table so it can be reprinted after 
  being moved
* Keep track of which table rows are handling split hands, so that 
  row can be removed after the round

I think the best option here is probably to have TerminalController 
keep a list of what data is in what field. DynamicUI changes the data 
in that list, and then TerminalController prints the data back to 
the UI. How big of a change is that? Pretty big, but doable.


The Players Leaving Problem
---------------------------
I want the game to feel, for lack of a better term, populated. It's 
not just the user playing against the computer dealer, there are other 
players at the table. They have victories and losses and make their 
own decisions, including whether to buy into the next round. This 
means I need to allow players to leave.

Now if players only leave, eventually the user will be alone with the 
dealer. That seems lonely. So, in addition to leaving, we need to 
allow players to join. But:

* How many can join?
* When can they join?
* Who are they?


How Many
~~~~~~~~
In order to simplify this, I decided a while ago to limit the game to 
a certain number of seats. That allows the UI to have an expectation 
of how many players it will have to display. I then proceded to code 
the game to expect a player in every seat.

There is a problem in that only the UI tracks seats. The game engine 
does not. However, it's the game engine that decides when players 
join. So, the only way the game engine can keep track of whether there 
is an open seat is if the action that removes a player also adds a 
new player.

That's probably a little awkward for the user. They see the "Walks 
away," message immediately followed by the join message. But is that 
worth fixing right now? I lean towards no. DynamicUI has a pause 
between events, so the user will have the opportunity to see the 
message, if briefly. Maybe I can allow empty seats in the future, but 
for now the casino is hoppin' and there are butts in every seat.


When
~~~~
Since the game engine needs it to be tied to the remove event, they 
join at the same time the old player leaves. This can be addressed in 
the future to give a game or two pause between players joining.


Who
~~~
The whole point of the random player generator was to make it random 
people. The question is, how many chips should they have. If it's 
fewer than the initial bet, they aren't going to be able to play this 
round anyway. So, that's the minimum. A couple of players walking up 
and walking away would be amusing. A potential infinite loop of them 
doing so is not.

So, the floor is Game.buyin. What is the ceiling? It probably should 
be random, but in a range. Since the big thing is whether or not they 
have enough for bets, maybe it should be based on some multiple of 
Game.buyin? Maybe the range is centered on 11 bets ± 10? That way 
you could get the player who walks up for one bet, busts then walks 
away.

So, that should be added to players.make_player().


Back to the UI
--------------
While the DynamicUI is now done, it feels over complicated. Right now 
it has three pieces:

* cli.DynamicUI: A class to implement the game.BaseUI class
* cli.TerminalController: A slightly more intuitive way of handling 
  the messages coming from game.Game, plus a way to maintain the 
  state of the UI
* run_terminal: A generator that allows UI events to happen within 
  blessed's fullscreen and hidden_cursor context managers

Each of those pieces are probably necessary to truly separate the game 
engine from the UI. The problem is that TerminalController should 
probably be more ignorant of the game events than it is. Right now it 
has a method per event sent by the game engine. It should probably 
only have methods relevant to the UI, letting DynamicUI translate 
between the engine and the UI.

That's doable, but what shape should the new TerminalController take? 
If I'm writing something to manage writing the game's UI to the 
terminal, maybe I should keep it open to be generically useful? Maybe?


termui
------
termui will be the new implementation of TerminalController. It will 
be in its own module. And:

* It will not have events specific to blackjack.
* It will maintain a tabular display of data in the terminal.
* It will handle user input.
* It will provide error handling to allow the recovery of exceptions 
  when the terminal is in fullscreen mode.

This will mean that DynamicUI will need to mediate between the game 
engine and TermController, but I think that is fine.

What user interface elements does termui need to deal with:

* Table title
* Description field
* Table headers
* Table frame
* Data cells
* Cell frames
* User prompt
* Errors

What events will termui need to handle:

* Initial draw
* Update cell
* Update frame
* Update table size
* Add row
* Add column
* Prompt user
* Update description
* Update title
* Error
* Display error
* Exit

There could be a page concept here, where the UI has multiple tables 
that the user can switch between. So, I need to be careful to allow 
multiple of the controller objects to exist at once, each one 
representing a page of the UI. Though, that sounds more like having 
one controller object and separate table objects holding each page, 
which is overkill at the moment, I think. Let's just focus on one 
table controller object now, and we can split table from controller 
in the future if needed.

Since it is controlling a table, though, I'll start by calling it 
Table.


Table Attributes
~~~~~~~~~~~~~~~~
What attributes does the Table object need:

* title
* description
* headers
* data
* frame_components
* header_templates
* cell_templates
* terminal
* prompt


Serializing UI
--------------
Serializing the game engine to save state raises a question, should 
the UI be serialized? I think the answer to this boil down to a 
separate question: what is the UI around game state restoration? 

This is a bit awkward since so far there isn't a concept of having a 
UI without an Engine object. I have to have a running Engine object to 
interact with the game at all, so I will need to have an Engine object 
before I prompt to load the saved game. That means once I have loaded 
the game state, I would have two Engines: the one that ran the restore 
dialog and the one that was restored.

I think, then, the solution to this is to not have the restore create 
a new game Engine. It uses the existing one with the existing UI. 
Rather than creating a new object, it reconfigures the existing Engine 
object and resets the UI. This likely has the side effect that I can't 
restore the game in the middle of a hand. That's probably fine. I 
wasn't looking to save state at points other than the end of hands 
anyway.

The upshot of all of this is that I don't need to worry about 
serializing UI object. I do need to make sure, though, that they 
can be reset after a game object is restored.

Another side effect of this that that the Engine object probably 
shouldn't have a deserialize() class method. It should be on the 
object, and I think I'll call it restore.


Range Validation
----------------
Bets and insurance have minimum and maximum valid values. However,
these aren't static ranges:

*   The bet range depends on the minimum and maximum bets set with
    the game,
*   The insurance range depends on the bet for the hand.

Current validations are handled in the model using data descriptors.
These descriptos are set on load, so they can't be easily changed
when the ranges for bets and insurance are known. Therefore validators
for those need to be a bit more flexible.

A descriptor may not be the right answer here. Descriptors seem best
for describing data types with a constant definition through the runtime
of the application. The range for insurance changes based on the size
of the player's bet. And, technically, the possible range of bets isn't
set until partway into the runtime of the program. Another answer is
likely needed.

For now, I'll put it in the relevant decision methods. That means the
Engine object will be trusting all decision methods will return a value
within the proper range. That's not ideal, so I may want to put extra
validation in in the future. However, for now, the decision methods
will handle it.

Actually, strike that. With the way the UI interaction is set up, it's
a mess to handle the prompting on a validation failure in the decision
method. So, instead, I'll go back to doing it in the Bet object. The
bet object will just have to do it with a property rather than with a
data descriptor.
