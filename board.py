from copy import deepcopy

MAX_X = 8
MAX_Y = 12
MAX_CARDS = 24
EMPTY_TILE = (0, 0)
_DEFAULT_BOARD = [[EMPTY_TILE for _ in range(MAX_Y)] for _ in range(MAX_X)]

R = 1  # Red
W = 2  # White
F = 1  # Full
O = 2  # Open

PLACEMENTS = {
    1: [((R, F), None), ((W, O), None)],  # Horizontal RF-WO
    2: [((W, O), (R, F)), (None, None)],  # Vertical RF-WO
    3: [((W, O), None), ((R, F), None)],  # Horizontal WO-RF
    4: [((R, F), (W, O)), (None, None)],  # Vertical WO-RF
    5: [((R, O), None), ((W, F), None)],  # Horizontal RO-WF
    6: [((W, F), (R, O)), (None, None)],  # Vertical RO-WF
    7: [((W, F), None), ((R, O), None)],  # Horizontal WF-RO
    8: [((R, O), (W, F)), (None, None)],  # Vertical WF-RO
}

X_LETTERS = {
    'A': 0,
    'B': 1,
    'C': 2,
    'D': 3,
    'E': 4,
    'F': 5,
    'G': 6,
    'H': 7,
}
X_LETTERS_INVERSE = {v: k for k, v in X_LETTERS.items()}

MAX_DEPTH = 3

KEY_GEN = {
    0: lambda move: (move.x, move.y),
    1: lambda move: (move.x + move.placement % 2, move.y + (move.placement + 1) % 2),
    2: lambda move: move.old_pos1,
    3: lambda move: move.old_pos2
}
VAL_GEN = {
    0: lambda move: move.card[0][0],
    1: lambda move: move.card[move.placement % 2][(move.placement + 1) % 2],
    2: lambda move: EMPTY_TILE,
    3: lambda move: EMPTY_TILE
}


def _count_tile(tile, count_red, count_white, count_full, count_open):
    if tile[0] == R:
        count_red += 1
        count_white = 0
    elif tile[0] == W:
        count_red = 0
        count_white += 1
    else:
        count_red = 0
        count_white = 0
    if tile[1] == F:
        count_full += 1
        count_open = 0
    elif tile[1] == O:
        count_full = 0
        count_open += 1
    else:
        count_full = 0
        count_open = 0
    return count_red, count_white, count_full, count_open


def _within_bounds(x, y, placement):
    return MAX_X - placement % 2 > x >= 0 and MAX_Y - (placement + 1) % 2 > y >= 0


def _str_tile(tile):
    # bg = '\033[0;38;41m {} \033[0m' if tile[0] == 1 else ('\033[0;38;47m {} \033[0m' if tile[0] == 2 else ' {} ')
    bg = 'R{}' if tile[0] == 1 else ('W{}' if tile[0] == 2 else ' {}')
    char = '•' if tile[1] == 1 else ('◦' if tile[1] == 2 else ' ')
    return bg.format(char)


def moves_to_positions(moves):
    return {KEY_GEN[pos](move): VAL_GEN[pos](move)
            for move in moves for pos in range(4 if move.type else 2)}


class GameBoard:

    def __init__(self):
        self._board = deepcopy(_DEFAULT_BOARD)
        self._moves = []
        self._num_moves = 0
        self.last_moved = None

    def __str__(self):
        # buff = '---' * 8 + '--'
        buff = '--' * 9
        for y in range(MAX_Y - 1, -1, -1):
            buff += '\n|'
            for x in range(MAX_X):
                buff += _str_tile(self._board[x][y])
            buff += '|'
        # buff += '\n' + '---' * 8 + '--'
        buff += '\n' + '--' * 9
        return buff

    def _apply(self, move):
        for x in range(2):
            for y in range(2):
                if not move.card[x][y]:
                    continue
                self._board[move.x + x][move.y + y] = move.card[x][y]

    def _space_avail(self, x, y, placement):
        """Checks that the given placement would not overlap existing placed cards"""
        into_tile = self._board[x][y]
        into_tile2 = self._board[x + placement % 2][y + (placement + 1) % 2]
        return into_tile == EMPTY_TILE and into_tile2 == EMPTY_TILE

    def _has_support(self, x, y, placement):
        """Checks that the given placement would not hang over an empty cell"""
        return y == 0 or (
                self._board[x][y - 1] != EMPTY_TILE and (placement % 2 == 0 or self._board[x + 1][y - 1] != EMPTY_TILE))

    def _verify_move(self, move):
        if not _within_bounds(move.x, move.y, move.placement):
            return Result({'within bounds': False})
        return Result({
            'has support': self._has_support(move.x, move.y, move.placement)
        })

    def _verify_add(self, move):
        """Checks that the given move would be a legal add"""
        result_move = self._verify_move(move)
        if not result_move.success:
            return result_move

        result = {
            'cards left': self._num_moves < MAX_CARDS,
            'space available': self._space_avail(move.x, move.y, move.placement),
        }
        result.update(result_move.conditions)
        return Result(result)

    def _add_card(self, move):
        result = self._verify_add(move)
        if result.success:
            self._apply(move)
        return result

    def _can_remove(self, move):
        """Checks that the card can be removed and keep the board state legal
        There cannot be additional cards placed above the one being moved
        """
        return self._board[move.old_pos1[0]][move.old_pos1[1] + 2] == EMPTY_TILE if \
            move.old_pos1[1] - move.old_pos2[1] == 0 else (
                self._board[move.old_pos1[0]][move.old_pos1[1] + 1] == EMPTY_TILE and
                self._board[move.old_pos1[0] + 1][move.old_pos1[1] + 1] == EMPTY_TILE)

    def _find_old_move(self, move):
        return [
            m for m in self._moves if
            move.old_pos1[0] == m.x and move.old_pos1[1] == m.y and (
                    m.x + m.placement % 2 == move.old_pos2[0] and m.y + (m.placement + 1) % 2 == move.old_pos2[1])
        ]

    def _verify_recycle(self, move):
        """Checks that the given move would a legal recycling"""
        result_move = self._verify_move(move)
        if not result_move.success:
            return result_move

        found = self._find_old_move(move)
        result = {
            'all cards placed': self._num_moves >= MAX_CARDS,
            'card exists': found,
            'can remove': self._can_remove(move),
            'different than last': not self.last_moved or (
                    self.last_moved.x != move.old_pos1[0] or self.last_moved.y != move.old_pos1[1]),
            'space available': (move.old_pos1[0] == move.x and move.old_pos1[1] == move.y and found
                                and not found[0].placement == move.placement) or self._space_avail(move.x, move.y,
                                                                                                   move.placement),
        }
        result.update(result_move.conditions)
        return Result(result)

    def _remove(self, old_move):
        self._moves.remove(old_move)
        self._board[old_move.x][old_move.y] = EMPTY_TILE
        self._board[old_move.x + old_move.placement % 2][old_move.y + (old_move.placement + 1) % 2] = EMPTY_TILE

    def _recycle_card(self, move):
        result = self._verify_recycle(move)
        if result.success:
            self._remove(result.conditions['card exists'][0])
            self._apply(move)
        return result

    def _win_diagonal(self):
        for x in range(MAX_X - 3):
            count_red = 0
            count_white = 0
            count_full = 0
            count_open = 0
            for offset in range(MAX_X - x):
                count_red, count_white, count_full, count_open = \
                    _count_tile(self._board[x + offset][offset], count_red, count_white, count_full, count_open)
                result = Result({
                    'red': count_red == 4,
                    'white': count_white == 4,
                    'full': count_full == 4,
                    'open': count_open == 4
                }, any)
                if result.success:
                    return result
        for y in range(1, MAX_Y - 3):
            count_red = 0
            count_white = 0
            count_full = 0
            count_open = 0
            for offset in range(min(MAX_X, MAX_Y - y)):
                count_red, count_white, count_full, count_open = \
                    _count_tile(self._board[offset][y + offset], count_red, count_white, count_full, count_open)
                result = Result({
                    'red': count_red == 4,
                    'white': count_white == 4,
                    'full': count_full == 4,
                    'open': count_open == 4
                }, any)
                if result.success:
                    return result

        # Reversed diagonal
        for x in range(MAX_X - 1, 2, -1):
            count_red = 0
            count_white = 0
            count_full = 0
            count_open = 0
            for offset in range(x + 1):
                count_red, count_white, count_full, count_open = \
                    _count_tile(self._board[x - offset][offset], count_red, count_white, count_full, count_open)
                result = Result({
                    'red': count_red == 4,
                    'white': count_white == 4,
                    'full': count_full == 4,
                    'open': count_open == 4
                }, any)
                if result.success:
                    return result
        for y in range(1, MAX_Y - 3):
            count_red = 0
            count_white = 0
            count_full = 0
            count_open = 0
            for offset in range(min(MAX_X, MAX_Y - y)):
                count_red, count_white, count_full, count_open = \
                    _count_tile(self._board[MAX_X - 1 - offset][y + offset], count_red, count_white, count_full,
                                count_open)
                result = Result({
                    'red': count_red == 4,
                    'white': count_white == 4,
                    'full': count_full == 4,
                    'open': count_open == 4
                }, any)
                if result.success:
                    return result
        return False

    def _win_horizontal(self):
        for y in range(MAX_Y):
            count_red = 0
            count_white = 0
            count_full = 0
            count_open = 0
            for x in range(MAX_X):
                count_red, count_white, count_full, count_open = \
                    _count_tile(self._board[x][y], count_red, count_white, count_full, count_open)
                result = Result({
                    'red': count_red == 4,
                    'white': count_white == 4,
                    'full': count_full == 4,
                    'open': count_open == 4
                }, any)
                if result.success:
                    return result

        return False

    def _win_vertical(self):
        for x in range(MAX_X):
            count_red = 0
            count_white = 0
            count_full = 0
            count_open = 0
            for y in range(MAX_Y):
                count_red, count_white, count_full, count_open = \
                    _count_tile(self._board[x][y], count_red, count_white, count_full, count_open)
                result = Result({
                    'red': count_red == 4,
                    'white': count_white == 4,
                    'full': count_full == 4,
                    'open': count_open == 4
                }, any)
                if result.success:
                    return result

        return False

    def is_winning_board(self):
        if self._num_moves >= 60:
            return Result({'draw': 'number of moves'})
        return self._win_diagonal() or self._win_horizontal() or self._win_vertical()

    def make_move(self, move):
        """Executes a move on the board, affecting state if the move is found to be legal"""
        result = self._recycle_card(move) if move.type else self._add_card(move)
        if result.success:
            self._moves.append(move)
            self.last_moved = move
            self._num_moves += 1
        return result

    def board_lookup(self, changed_positions, x, y):
        """Looks up a position on the board, accounting for forecasted moves"""
        return changed_positions.get((x, y)) or self._board[x][y]

    def _max_height_for_x(self, x, changed_positions):
        """Finds the height of the highest empty tile in the given column"""
        for y in range(MAX_Y):
            if self.board_lookup(changed_positions, x, y) == EMPTY_TILE:
                return y
        return MAX_Y

    def _generate_add_moves(self, changed_positions):
        """Looks at every position on the board where a card can be added on top"""
        for x in range(MAX_X):
            y = self._max_height_for_x(x, changed_positions)

            if y < MAX_Y - 1:
                yield from (Move(0, placement, x, y) for placement in [2, 4, 6, 8])

            if x < MAX_X - 1 and MAX_Y > y == self._max_height_for_x(x + 1, changed_positions):
                yield from (Move(0, placement, x, y) for placement in [1, 3, 5, 7])

    def _can_recycle_move(self, move, changed_positions):
        return self.board_lookup(changed_positions, move.x, move.y + 2) == EMPTY_TILE if \
            move.placement % 2 else (
                self._board[move.x][move.y + 1] == EMPTY_TILE and
                self._board[move.x + 1][move.y + 1] == EMPTY_TILE
        )

    def _generate_recycle_moves(self, moves, changed_positions):
        """Looks at every placed card that can be removed, then looks at every possible replacement for each card"""
        recyclable_moves = [move for move in (self._moves + moves)[:-1] if
                            self._can_recycle_move(move, changed_positions)]
        for move in recyclable_moves:
            old_pos1 = (move.x, move.y)
            old_pos2 = (move.x + move.placement % 2, move.y + (move.placement - 1) % 2)
            _changed_positions = changed_positions.copy()
            _changed_positions.update({
                old_pos1: EMPTY_TILE,
                old_pos2: EMPTY_TILE
            })
            for x in range(MAX_X):
                y = self._max_height_for_x(x, _changed_positions)

                if y < MAX_Y - 1:
                    yield from (Move(1, placement, x, y, old_pos1, old_pos2) for placement in [2, 4, 6, 8])

                if x < MAX_X - 1 and MAX_Y > y == self._max_height_for_x(x + 1, _changed_positions):
                    yield from (Move(1, placement, x, y, old_pos1, old_pos2) for placement in [1, 3, 5, 7])

    def _generate_moves(self, moves):
        """Returns a generator for all possible moves with the current board state and given forecasted moves"""
        changed_positions = moves_to_positions(moves)

        if self._num_moves + len(moves) < MAX_CARDS:
            return self._generate_add_moves(changed_positions)
        return self._generate_recycle_moves(moves, changed_positions)

    def possible_moves(self, moves=None, level=1):
        if level < MAX_DEPTH - 1:
            return {move: self.possible_moves(moves + [move] if moves else [move], level + 1)
                    for move in self._generate_moves(moves or [])}
        return list(self._generate_moves(moves))  # Max depth reached


class Move:
    @staticmethod
    def from_str(str_):
        args = str_.split(' ')
        if args[0] == '0':
            _, placement, x, y = args
            placement = int(placement)
            x = X_LETTERS[x]
            y = int(y) - 1
            return Move(0, placement, x, y)
        else:
            old_x1, old_y1, old_x2, old_y2, placement, x, y = args
            x = X_LETTERS[x]
            y = int(y) - 1
            placement = int(placement)
            old_pos1 = (X_LETTERS[old_x1], int(old_y1) - 1)
            old_pos2 = (X_LETTERS[old_x2], int(old_y2) - 1)
            return Move(1, placement, x, y, old_pos1, old_pos2)

    def __init__(self, type_, placement, x, y, old_pos1=(-1, -1), old_pos2=(-1, -1)):
        self.type = type_  # 0 for add, 1 for recycling
        self.placement = placement
        self.card = PLACEMENTS[placement]
        self.x = x
        self.y = y
        self.old_pos1 = old_pos1
        self.old_pos2 = old_pos2

    def __str__(self):
        if self.type:
            return '{} {} {} {} {} {} {}'.format(X_LETTERS_INVERSE[self.old_pos1[0]], self.old_pos1[1] + 1,
                                                 X_LETTERS_INVERSE[self.old_pos2[0]], self.old_pos2[1] + 1,
                                                 self.placement, X_LETTERS_INVERSE[self.x], self.y + 1)
        return '{} {} {} {}'.format(self.type, self.placement, X_LETTERS_INVERSE[self.x], self.y + 1)

    def __hash__(self):
        """Recycling moves: 1000000 to 7118711710
        Add moves: 1 to 7118"""
        if self.type:
            return self.x * 10 ** 9 + self.y * 10 ** 7 + self.placement * 10 ** 6 + \
                   self.old_pos1[0] * 10 ** 5 + self.old_pos1[1] * 10 ** 3 + \
                   self.old_pos2[0] * 10 ** 2 + self.old_pos2[1]
        return self.x * 10 ** 3 + self.y * 10 + self.placement

    def __eq__(self, other):
        return isinstance(other, Move) and \
               self.x == other.x and \
               self.y == other.y and \
               self.placement == other.placement and \
               self.type == other.type and \
               self.old_pos1 == other.old_pos1 and \
               self.old_pos2 == other.old_pos2


class Result:
    def __init__(self, conditions, eval_=all):
        self.conditions = conditions
        self.success = eval_(conditions.values())
