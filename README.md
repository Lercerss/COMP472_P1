# COMP 472 Winter 2019 Project 1
Simulates the "Double Card Game" and allows users to play against a minimax algorithm.

## Usage
Start the game by running `python3 main.py` from the terminal.

## Example moves
__Adding:__  
Add moves must start with a `0`, then followed by the placement of the card (1-8) and the bottom-left position of 
where the card should be placed.
 - `0 3 A 1`
 - `0 7 C 1`
 - `0 4 E 1`
 - `0 5 C 2`
 - `0 1 C 2`
 - `0 4 F 1`
 - `0 8 G 2` 

__Recycling:__  
Recycling moves must indicate which card to move by designating both of its positions, then a new placement and a new 
bottom-left position. Recycling moves are only legal once all 24 cards have been placed.
 - `A 3 A 4 2 G 1` moves card at A3-A4 to G1 with placement 2
 - `F 6 G 6 6 A 10` moves card at F6-G6 to A10 with placement 6