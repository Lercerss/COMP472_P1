from unittest import TestCase

from board import R, W, F, O, EMPTY_TILE, GameBoard, Move
from heuristics import _count_sequence, informed, INF
from minimax import MiniMax


class CountTests(TestCase):

    def testWinning(self):
        sequence = [(R, F), (R, F), (R, F), (R, F)]
        self.assertEqual((4, 4), _count_sequence(sequence))

        sequence = [(R, F), (R, F), (R, O), (R, F)]
        self.assertEqual((4, 0), _count_sequence(sequence))

    def testCountTriple(self):
        sequence = [(R, F), (R, F), EMPTY_TILE, (R, F)]
        self.assertEqual((3, 3), _count_sequence(sequence))

        sequence = [(R, F), (R, F), (R, F), EMPTY_TILE]
        self.assertEqual((3, 3), _count_sequence(sequence))

    def testCountDouble(self):
        sequence = [(W, O), (W, O), EMPTY_TILE, EMPTY_TILE]
        self.assertEqual((2, 2), _count_sequence(sequence))

        sequence = [(W, O), EMPTY_TILE, EMPTY_TILE, (W, O)]
        self.assertEqual((2, 2), _count_sequence(sequence))


class InformedTest(TestCase):
    def setUp(self):
        self.board = GameBoard()

    def testEmpty(self):
        self.assertEqual(0, informed(self.board, [], 0))

    def testWinning(self):
        self.board.make_move(Move(0, 2, 0, 0))
        self.board.make_move(Move(0, 2, 1, 0))
        self.board.make_move(Move(0, 2, 2, 0))
        self.board.make_move(Move(0, 2, 3, 0))
        self.assertEqual(INF, informed(self.board, [], 1))

        self.board = GameBoard()
        self.board.make_move(Move(0, 1, 0, 0))
        self.board.make_move(Move(0, 1, 0, 1))
        self.board.make_move(Move(0, 1, 0, 2))
        self.board.make_move(Move(0, 1, 0, 3))
        self.assertEqual(INF, informed(self.board, [], 1))
        self.assertEqual(-INF, informed(self.board, [], 0))

        self.board = GameBoard()
        self.board.make_move(Move(0, 1, 0, 0))
        self.board.make_move(Move(0, 7, 0, 1))
        self.board.make_move(Move(0, 1, 2, 0))
        self.board.make_move(Move(0, 5, 2, 1))
        self.board.make_move(Move(0, 1, 2, 2))
        self.board.make_move(Move(0, 3, 2, 3))
        self.assertEqual(INF, informed(self.board, [], 0))
        self.assertEqual(INF, informed(self.board, [], 1))

        self.board = GameBoard()
        self.board.make_move(Move(0, 1, 2, 0))
        self.board.make_move(Move(0, 7, 2, 1))
        self.board.make_move(Move(0, 1, 0, 0))
        self.board.make_move(Move(0, 5, 0, 1))
        self.board.make_move(Move(0, 1, 0, 2))
        self.board.make_move(Move(0, 3, 0, 3))
        self.assertEqual(INF, informed(self.board, [], 0))
        self.assertEqual(INF, informed(self.board, [], 1))

    def testRandom(self):
        self.board.make_move(Move(0, 3, 0, 0))
        self.board.make_move(Move(0, 2, 2, 0))
        self.board.make_move(Move(0, 4, 3, 0))
        self.board.make_move(Move(0, 8, 4, 0))
        self.board.make_move(Move(0, 8, 7, 0))
        self.board.make_move(Move(0, 4, 6, 0))
        self.assertEqual(370, informed(self.board, [], 1))

    def testMovesWinning(self):
        self.board.make_move(Move(0, 1, 0, 0))
        self.board.make_move(Move(0, 1, 0, 1))
        self.board.make_move(Move(0, 1, 0, 2))
        self.assertEqual(-INF, informed(self.board, [Move(0, 1, 0, 3), Move(0, 1, 2, 0)], 1))

        self.board = GameBoard()
        self.board.make_move(Move(0, 1, 0, 0))
        self.board.make_move(Move(0, 3, 0, 1))
        self.board.make_move(Move(0, 1, 2, 0))
        self.board.make_move(Move(0, 5, 2, 1))
        self.assertEqual(-INF, informed(self.board, [Move(0, 1, 2, 2), Move(0, 3, 2, 3)], 0))
        self.assertEqual(INF, informed(self.board, [Move(0, 1, 2, 2), Move(0, 3, 2, 3)], 1))
        self.assertEqual(-INF, informed(self.board,
                                        [Move(0, 1, 6, 0), Move(0, 1, 2, 2), Move(0, 3, 2, 3), Move(0, 1, 6, 1)],
                                        1))


class MiniMaxTests(TestCase):
    def setUp(self):
        self.board = GameBoard()

    def testWinBoard(self):
        self.board.make_move(Move(0, 7, 1, 0))
        self.board.make_move(Move(0, 3, 1, 1))
        self.board.make_move(Move(0, 7, 1, 2))
        result = MiniMax(['red', 'white']).make_move(self.board, None)
        self.assertTrue(result.success)
        win = self.board.is_winning_board()
        self.assertTrue(win.success)
        self.assertIn([key for key, value in win.conditions.items() if value][0], ['red', 'white'])

    def testDenyWinBoard(self):
        self.board.make_move(Move(0, 7, 1, 0))
        self.board.make_move(Move(0, 3, 1, 1))
        self.board.make_move(Move(0, 7, 1, 2))
        result = MiniMax(['full', 'open']).make_move(self.board, None)
        self.assertTrue(result.success)
        win = self.board.is_winning_board()
        self.assertFalse(win)
