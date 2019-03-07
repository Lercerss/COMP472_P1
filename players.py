import re

from board import Move
from minimax import MiniMax

ADD_MOVE_FORMAT = r'^0 [1-8] [A-H] ([1-9]|1[012])$'
_add_format = re.compile(ADD_MOVE_FORMAT)
RECYCLE_FORMAT = r'^[A-H] ([1-9]|1[012]) [A-H] ([1-9]|1[012]) [1-8] [A-H] ([1-9]|1[012])$'
_rec_format = re.compile(RECYCLE_FORMAT)


class Player:
    def __init__(self, name, is_human, win_condition):
        self.name = name
        self.is_human = is_human
        self.move = self._player_move if is_human else MiniMax(win_condition).make_move
        self.condition = win_condition

    def _player_move(self, board, _):
        prompt = '({}) Enter next move: '.format(self.name)
        move = input(prompt)

        while not (_add_format.match(move) or _rec_format.match(move)):
            print('Invalid format, expecting: ' + ADD_MOVE_FORMAT + ' or ' + RECYCLE_FORMAT)
            move = input(prompt)

        return board.make_move(Move.from_str(move))
