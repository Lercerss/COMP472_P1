from math import isnan, isinf

from board import R, W, F, O, MAX_X, MAX_Y, EMPTY_TILE, moves_to_positions

_NAIVE_WEIGHTS = {
    (R, F): -2,
    (R, O): -1.5,
    (W, F): 3,
    (W, O): 1,
}
SEQUENCE_LENGTH = 4
DIRECTION_X = 1
DIRECTION_Y = 1 << 1
DIRECTION_REVERSED = 1 << 2
INF = float('inf')

WEIGHTS = [0, 1, 10, 100, INF]


def _count_sequence(sequence):
    """Looks at given sequence to determine how close that sequence is to a winning sequence
    0 for an impossible win or no progress
    1-3 for the corresponding number of tiles towards a winning sequence
    4 for a winning sequence
    """
    count_color, count_dot = 0, 0
    color = 0
    dot = 0

    for tile in sequence:
        if tile == EMPTY_TILE:
            continue

        if tile[0] == R:
            if color == W:
                count_color = 0
                color = -1
            elif color > -1:
                count_color += 1
                color = R
        if tile[0] == W:
            if color == R:
                count_color = 0
                color = -1
            elif color > -1:
                count_color += 1
                color = W

        if tile[1] == F:
            if dot == O:
                count_dot = 0
                dot = -1
            elif dot > -1:
                count_dot += 1
                dot = F
        if tile[1] == O:
            if dot == F:
                count_dot = 0
                dot = -1
            elif dot > -1:
                count_dot += 1
                dot = O

    return count_color, count_dot


def _make_sequence(board, changed_positions, x, y, direction):
    return [board.board_lookup(changed_positions,
                               x + i * (direction & DIRECTION_X) * ([1, -1][bool(direction & DIRECTION_REVERSED)]),
                               y + i * bool(direction & DIRECTION_Y))
            for i in range(SEQUENCE_LENGTH)]


def _simple_iterate(board, moves, fn):
    changed_positions = moves_to_positions(moves)
    e = 0
    for x in range(MAX_X):
        for y in range(MAX_Y):
            tile = board.board_lookup(changed_positions, x, y)
            if tile == EMPTY_TILE:
                break
            e += fn(tile, x, y)
    return e


def _sequences_iterate(board, moves, fn):
    changed_positions = moves_to_positions(moves)
    e = 0
    wins = set()

    def fn_sequence(x, y, direction):
        val = fn(_make_sequence(board, changed_positions, x, y, direction))
        if isinf(val) or isnan(val):
            wins.add((x, y))
        return val

    for x in range(MAX_X):
        for y in range(MAX_Y):
            if y < MAX_Y - 3:
                e += fn_sequence(x, y, DIRECTION_Y)

            if x < MAX_X - 3:
                e += fn_sequence(x, y, DIRECTION_X)

            if x < MAX_X - 3 and y < MAX_Y - 3:
                e += fn_sequence(x, y, DIRECTION_X | DIRECTION_Y)

            if x >= 3 and y < MAX_Y - 3:
                e += fn_sequence(x, y, DIRECTION_X | DIRECTION_Y | DIRECTION_REVERSED)

    return e, wins


def naive(board, moves):
    def naive_count(tile, x, y):
        return _NAIVE_WEIGHTS[tile] * (y * 10 + x + 1)

    return _simple_iterate(board, moves, naive_count)


def informed(board, moves, condition):
    def sequence_eval(sequence):
        count_color, count_dot = _count_sequence(sequence)
        return WEIGHTS[count_color] - WEIGHTS[count_dot]

    val, wins = _sequences_iterate(board, moves, sequence_eval)
    if not isnan(val):
        return val

    # Board is in a winning state for both players, need to determine tiebreaker
    for i in range(len(moves)):
        sub_val, _ = _sequences_iterate(board, moves[:i + 1], sequence_eval)
        if isinf(sub_val) or isnan(sub_val):
            return INF * (-1, 1)[(condition + len(moves) - i - 1) % 2]

    return INF * (-1, 1)[condition]
