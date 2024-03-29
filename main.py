from contextlib import contextmanager

from board import GameBoard, Result
from players import Player


@contextmanager
def _no_context():
    yield None


def win_condition():
    prompt = 'Player 1 will play for dots or colors? (D/C): '
    conditions = {
        'D': ['full', 'open'],
        'C': ['red', 'white']
    }
    opposite = {
        'C': ['full', 'open'],
        'D': ['red', 'white']
    }
    cond = input(prompt)
    while not cond or cond[0].upper() not in conditions.keys():
        print('Invalid input, expecting: ' + str('/'.join(conditions.keys())))
        cond = input(prompt)

    return conditions[cond[0].upper()], opposite[cond[0].upper()]


def setup():
    prompt = 'Will you play the game against another player? (Y/N): '
    computer = input(prompt)
    while not computer or computer[0].upper() not in ('Y', 'N'):
        print('Invalid input, expecting: (Y/N)')
        computer = input(prompt)
    computer = computer[0].upper() == 'N'

    first = False
    trace_file_path = None
    if computer:
        prompt = 'File name for trace? (Empty for no trace): '
        trace_file_path = input(prompt)

        prompt = 'Who goes first, player or computer? (P/C): '
        first = input(prompt)
        while not first or first[0].upper() not in ('P', 'C'):
            print('Invalid input, expecting: (P/C)')
            first = input(prompt)
        first = first[0].upper() == 'C'

    p1_condition, p2_condition = win_condition()
    return [Player('P1', not computer or not first, p1_condition),
            Player('P2', not computer or first, p2_condition)], trace_file_path


def main():
    print('Welcome to the Double Card game!')
    current_player = 0
    players, trace_file_path = setup()
    board = GameBoard()
    game_result = None
    with open(trace_file_path, 'w') if trace_file_path else _no_context() as file:
        while not game_result or not game_result.success:
            result = players[current_player % 2].move(board, file)

            while players[current_player % 2].is_human and not result.success:
                print('Move not legal, please enter a different move. (reasons: {})'.format(
                    ['{}:{}'.format(key, value) for key, value in result.conditions.items() if not value]))
                result = players[current_player % 2].move(board, file)

            if not result.success:
                print('Failed to get valid move for player {}.'.format(current_player % 2 + 1))
                game_result = Result({players[(current_player + 1) % 2].condition[0]: True})  # Lose the game
                break

            print(str(board))
            current_player += 1
            game_result = board.is_winning_board()

    winning = [key for key, value in game_result.conditions.items() if value]
    if any(k in players[(current_player - 1) % 2].condition for k in winning):
        print('Player {} has won the game!'.format((current_player - 1) % 2 + 1))
    elif any(k in players[current_player % 2].condition for k in winning):
        print('Player {} has won the game!'.format(current_player % 2 + 1))
    else:
        print('Game is a tie! ({})'.format(game_result.conditions.get('draw', 'invalid')))


if __name__ == '__main__':
    main()
