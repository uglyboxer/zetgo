import os
from zetgo.board import Board

'''
Play will start with:
imagine_move(pos, color)
imagine_zobrist(pos, color)
if legal:
    position.occupy(color)
    if no friendly dragons, make one
        update board dragon list
    add move to dragon, stitch friendly dragons
    update enemy dragons
pass ?
    2nd pass ?
        y == q
if not:
    self.previous_pass = False
switch player

'''


class Game(object):

    def __init__(self, board_size=19):

        self.board = Board(board_size=board_size)
        self.passes = [False, False]
        self.captures = {1: 0, -1: 0}

    def add_up_score(self, player, dragons):
        for d in dragons:
            self.captures[player] += len(d.members)

    def score(self):
        rv = self.board.set_empty_dragons()
        for x in [-1, 1]:
            self.add_up_score(x, rv[x])
        return {'captures': self.captures}

    def move(self, move):
        result = {'complete': False,
                  'valid': True,
                  'captures': self.captures}
        try:
            if move == 'p':
                if self.passes[0]:
                    self.passes[1] = True
                    result['complete'] = True
                else:
                    self.passes[0] = True
                    self.board.switch_player()
                return result
            x, y = convert_from_str(move)
        except ValueError:
            print('Need input of the form: int, int')
            result['valid'] = False
            return result
        else:
            result = self.board.act((x, y))
            if not result['valid']:
                return result
            self.captures[1] += result['captures'][1]
            self.captures[-1] += result['captures'][-1]
            self.passes[0] = False
        self.board.switch_player()
        result['captures'] = self.captures
        return result


def convert_from_str(move):
    x, y = move.split(',')
    x = int(x.strip())
    y = int(y.strip())
    return x, y


# TODO break up this function and provide api for bot or viz
# TODO provide a list of possible moves for action space
def start_game():
    game = Game(BOARD_SIZE)
    os.system("clear")
    print(game.board.to_ascii())
    print(game.captures)
    while not game.passes[1]:
        move = input('{} please place stone: '.format(game.board.current_player))
        rv = game.move(move)
        if rv['complete']:
            game.score()
            break
        elif not rv:
            continue
        os.system("clear")
        print(game.board.to_ascii())
        print(game.captures)


if __name__ == '__main__':
    start_game()
