# Wumpus
Play the Wumpus game -- avoid pits and the Wumpus and find the gold

Propostional logic (knowledge base, resolution method and queries) are handled via functions from AIMA found in:<br />
https://github.com/aimacode/aima-python/blob/master/logic.py<br />
http://aima.cs.berkeley.edu/python/utils.html

The path of the agent moving through the game, searching for the gold, is shown in printout below. The initial board configuration is:

```
--------------------
     -  -  G  P 
     W  -  P  - 
     -  -  -  - 
     A  -  P  - 
--------------------
```
where "A" is the agent, "W" is the Wumpus, "P" are pits, and "G" is the gold. The agent has to find the gold while avoiding the pits and the Wumpus. At the start of each move, sensors provide some data:<br />

breeze:  indicates a pit is in a neighboring cell<br />
stench:  indicates the Wumpus is in a neighboring cell<br />
glitter: indicates the gold is in a neighboring cell<br />

There are four blocks of information shown for each move:

**Determinations**

What I know so far (pits, wumpus, gold) based on the sensor data (breeze, stench, and glitter) coupled with propositional logic. Initially, I know nothing.

0 = definitely nothing is in the cell<br />
1 = maybe something is in the cell<br />
2 = definitely something is in the cell<br />

Examples:

PWG = Pit / Wumpus / Gold -- obtained by  KB |- alpha queries

010: cell might contain a wumpus (i.e. risky),
     but doesn't contain a pit or gold.<br />
200: cell contains a pit, but no wumpus or gold<br />
000: cell is completely safe -- neither a pit, wumpus, nor gold.<br />
111: anything could be in the cell (i.e. risky).<br />

**Sensor Data**

What I observed when visiting the cell.<br />

B = breeze, S = stench, G = glitter<br />

This data is used to make the determinations through logic.

**Move Order**

Shows the order of the agent's moves throughout the game. The agent can backtrack at any point and move to a new cell that is a neighbor of any previously visited cell.

**Hidden View**

This shows where the agent, gold, pits and wumpus are. Of course, I'm not using any of this information in the move strategy, it's just listed for demonstration purposes (and useful during debugging).

```
Start of Game
------------------------------------------------------------------------
  Determinations           Sensor Data         Move Order    Hidden View
111  111  111  111     ---  ---  ---  ---      0  0  0  0     -  -  G  P 
111  111  111  111     ---  ---  ---  ---      0  0  0  0     W  -  P  - 
111  111  111  111     ---  ---  ---  ---      0  0  0  0     -  -  -  - 
111  111  111  111     ---  ---  ---  ---      0  0  0  0     -  -  P  - 
------------------------------------------------------------------------
Move # 1 -- to (1, 1): Safe
------------------------------------------------------------------------
  Determinations           Sensor Data         Move Order    Hidden View
111  111  111  111     ---  ---  ---  ---      0  0  0  0     -  -  G  P 
111  111  111  111     ---  ---  ---  ---      0  0  0  0     W  -  P  - 
000  111  111  111     ---  ---  ---  ---      0  0  0  0     -  -  -  - 
000  000  111  111     ---  ---  ---  ---      1  0  0  0     A  -  P  - 
------------------------------------------------------------------------
Move # 2 -- to (1, 2): safe, detect stench
------------------------------------------------------------------------
  Determinations           Sensor Data         Move Order    Hidden View
111  111  111  111     ---  ---  ---  ---      0  0  0  0     -  -  G  P 
010  111  111  111     ---  ---  ---  ---      0  0  0  0     W  -  P  - 
000  010  111  111     -S-  ---  ---  ---      2  0  0  0     A  -  -  - 
000  000  111  111     ---  ---  ---  ---      1  0  0  0     -  -  P  - 
------------------------------------------------------------------------
Move # 3 -- to (2, 1): safe, detect breeze
------------------------------------------------------------------------
  Determinations           Sensor Data         Move Order    Hidden View
111  111  111  111     ---  ---  ---  ---      0  0  0  0     -  -  G  P 
020  111  111  111     ---  ---  ---  ---      0  0  0  0     W  -  P  - 
000  000  111  111     -S-  ---  ---  ---      2  0  0  0     -  -  -  - 
000  000  200  111     ---  B--  ---  ---      1  3  0  0     -  A  P  - 
------------------------------------------------------------------------
Move # 4 -- to (2, 2): safe
------------------------------------------------------------------------
  Determinations           Sensor Data         Move Order    Hidden View
111  111  111  111     ---  ---  ---  ---      0  0  0  0     -  -  G  P 
020  000  111  111     ---  ---  ---  ---      0  0  0  0     W  -  P  - 
000  000  000  111     -S-  ---  ---  ---      2  4  0  0     -  A  -  - 
000  000  200  111     ---  B--  ---  ---      1  3  0  0     -  -  P  - 
------------------------------------------------------------------------
Move # 5 -- to (2, 3): safe, detect breeze & stench
------------------------------------------------------------------------
  Determinations           Sensor Data         Move Order    Hidden View
111  110  111  111     ---  ---  ---  ---      0  0  0  0     -  -  G  P 
020  000  110  111     ---  BS-  ---  ---      0  5  0  0     W  A  P  - 
000  000  000  111     -S-  ---  ---  ---      2  4  0  0     -  -  -  - 
000  000  200  111     ---  B--  ---  ---      1  3  0  0     -  -  P  - 
------------------------------------------------------------------------
Move # 6 -- to (3, 2): safe, detect breeze
------------------------------------------------------------------------
  Determinations           Sensor Data         Move Order    Hidden View
111  110  111  111     ---  ---  ---  ---      0  0  0  0     -  -  G  P 
020  000  100  111     ---  BS-  ---  ---      0  5  0  0     W  -  P  - 
000  000  000  100     -S-  ---  B--  ---      2  4  6  0     -  -  A  - 
000  000  200  111     ---  B--  ---  ---      1  3  0  0     -  -  P  - 
------------------------------------------------------------------------
Move # 7 -- to (2, 4): risky, detect glitter
------------------------------------------------------------------------
  Determinations           Sensor Data         Move Order    Hidden View
001  000  001  111     ---  --G  ---  ---      0  7  0  0     -  A  G  P 
020  000  200  111     ---  BS-  ---  ---      0  5  0  0     W  -  P  - 
000  000  000  100     -S-  ---  B--  ---      2  4  6  0     -  -  -  - 
000  000  200  111     ---  B--  ---  ---      1  3  0  0     -  -  P  - 
------------------------------------------------------------------------
Move # 8 -- to (1, 4): safe, detect stench
------------------------------------------------------------------------
  Determinations           Sensor Data         Move Order    Hidden View
000  000  002  111     -S-  --G  ---  ---      8  7  0  0     A  -  G  P 
020  000  200  111     ---  BS-  ---  ---      0  5  0  0     W  -  P  - 
000  000  000  100     -S-  ---  B--  ---      2  4  6  0     -  -  -  - 
000  000  200  111     ---  B--  ---  ---      1  3  0  0     -  -  P  - 
------------------------------------------------------------------------
Move # 9 -- to (3, 4): gold, detect breeze
Game Won!
------------------------------------------------------------------------
  Determinations           Sensor Data         Move Order    Hidden View
000  000  002  111     -S-  --G  B--  ---      8  7  9  0     -  -  A  P 
020  000  200  111     ---  BS-  ---  ---      0  5  0  0     W  -  P  - 
000  000  000  100     -S-  ---  B--  ---      2  4  6  0     -  -  -  - 
000  000  200  111     ---  B--  ---  ---      1  3  0  0     -  -  P  - 
------------------------------------------------------------------------
```
