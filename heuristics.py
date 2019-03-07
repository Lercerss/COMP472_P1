from board import R, W, F, O, MAX_X, MAX_Y, EMPTY_TILE, moves_to_positions

_NAIVE_WEIGHTS = {
    (R, F): -2,
    (R, O): -1.5,
    (W, F): 3,
    (W, O): 1,
}


def _simple_count(board, moves, fn):
    changed_positions = moves_to_positions(moves)
    e = 0
    for x in range(MAX_X):
        for y in range(MAX_Y):
            tile = board.board_lookup(changed_positions, x, y)
            if tile == EMPTY_TILE:
                break
            e += fn(tile, x, y)
    return e


def naive(board, moves):
    def naive_count(tile, x, y):
        return _NAIVE_WEIGHTS[tile] * (y * 10 + x + 1)

    return _simple_count(board, moves, naive_count)
