from heuristics import naive


class MiniMax:

    def __init__(self, win_condition):
        self._reset()
        self._win_condition = 'full' in win_condition

    def _reset(self):
        self._num_evals = 0
        self._level_2_nodes = []

    def _trace(self, trace_file, e):
        if trace_file:
            trace_file.writelines(
                [str(self._num_evals), '\n{:.1f}\n\n'.format(e)] +
                ['{:.1f}\n'.format(val) for val in self._level_2_nodes] +
                ['\n']
            )

    def _min_max(self, level, sub_results):
        fn = (min, max)[(level + self._win_condition) % 2]  # Color maximizes, dots minimize
        return fn(sub_results.items())

    def _evaluate(self, board, possible_moves, path=None, level=1):
        """Recursively walks the state tree and determines the e(n) for each node
        Returns the best node's e(n) and its path"""
        if isinstance(possible_moves, dict):  # Not deepest level of tree
            path = path or []
            sub_results = {}
            for move, next_level in possible_moves.items():
                e, result_path = self._evaluate(board, next_level, path=path + [move], level=level + 1)
                sub_results[e] = result_path
                if level == 1:
                    self._level_2_nodes.append(e)
            return self._min_max(level, sub_results)

        # Deepest level is a list of moves instead of a dict
        sub_results = {naive(board, path + [move]): path + [move] for move in possible_moves}
        self._num_evals += len(possible_moves)
        return self._min_max(level, sub_results)

    def make_move(self, board, trace_file):
        self._reset()

        e, best_moves = self._evaluate(board, board.possible_moves())
        self._trace(trace_file, e)

        print("Found path: {}".format([str(move) for move in best_moves]))
        print("Computer move: {}".format(best_moves[0]))

        return board.make_move(best_moves[0])
