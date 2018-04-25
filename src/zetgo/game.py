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
        self.current_player = 1  # TODO, accept handicaps and set this to 'w'
        self.passes = [False, False]
        self.captures = {1: 0, -1: 0}

    def switch_player(self):
        self.current_player = self.current_player * -1

    def add_up_score(self, player, dragons):
        for d in dragons:
            self.captures[player] += len(d.members)

    def score(self):
        rv = self.board.set_empty_dragons()
        for x in [-1, 1]:
            self.add_up_score(x, rv[x])
        return {'captures': self.captures}

    def move(self, move):
        board = self.board
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
                    self.switch_player()
                return result
            x, y = convert_from_str(move)
        except ValueError:
            print('Need input of the form: int, int')
            result['valid'] = False
            return result
        else:
            # The below should be a board method
            pos = board.pos_by_location((x, y))
            rv = board.imagine_position(pos, self.current_player)
            if rv['occupied'] or rv['suicide'] or rv['repeat']:
                result['valid'] = False
                return result
            friendly_dragons = list(rv['stitched'])
            touched_dragons = set()
            pos.occupy(self.current_player)
            if not friendly_dragons:
                dragon_id = board.create_new_dragon()
                board.dragons[dragon_id].add_member(pos)
                touched_dragons.add(board.dragons[dragon_id])
            else:
                base_dragon = friendly_dragons[0]
                base_dragon.add_member(pos)
                for dragon in friendly_dragons[1:]:
                    board.stitch_dragons(base_dragon.identifier, dragon.identifier)
                touched_dragons.add(base_dragon)
            if rv['captured']:
                for dragon in rv['captured']:
                    self.captures[self.current_player] += board.capture_dragon(dragon.identifier)

            touched_dragons.update(rv['opp_neighbor'])
            for dragon in touched_dragons:
                dragon.update()

            board.z_table.add(rv['zhash'])
            self.passes[0] = False
        self.switch_player()
        result['captures'] = self.captures
        return result

    def play(self):
        board = self.board
        print(board.to_ascii())
        while not self.passes[1]:
            move = input('{} please place stone: '.format(self.current_player))
            try:
                if move == 'p':
                    if self.passes[0]:
                        self.passes[1] = True
                    else:
                        self.passes[0] = True
                x, y = convert_from_str(move)
            except ValueError:
                print('Need input of the form: int, int')
                continue
            else:
                pos = board.pos_by_location((x, y))
                if pos.is_occupied:
                    continue
                rv = board.imagine_position(pos, self.current_player)
                print(rv)
                if rv['suicide']:
                    continue
                # TODO imagine zoborist
                friendly_dragons = list(rv['stitched'])
                touched_dragons = set()
                pos.occupy(self.current_player)
                if not friendly_dragons:
                    dragon_id = board.create_new_dragon()
                    board.dragons[dragon_id].add_member(pos)
                    touched_dragons.add(board.dragons[dragon_id])
                else:
                    base_dragon = friendly_dragons[0]
                    base_dragon.add_member(pos)
                    for dragon in friendly_dragons[1:]:
                        board.stitch_dragons(base_dragon.identifier, dragon.identifier)
                    touched_dragons.add(base_dragon)
                if rv['captured']:
                    for dragon in rv['captured']:
                        self.captures[self.current_player] += board.capture_dragon(dragon.identifier)

                touched_dragons.update(rv['opp_neighbor'])
                for dragon in touched_dragons:
                    dragon.update()
                self.passes[0] = False
            self.switch_player()
            print(board.to_ascii())
            print(self.captures)
        self.score()


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
        move = input('{} please place stone: '.format(game.current_player))
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
