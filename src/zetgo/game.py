from board import Board


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
        self.current_player = 'b'  # TODO, accept handicaps and set this to 'w'
        self.passes = [False, False]
        self.captures = {'b': 0, 'w': 0}

    def switch_player(self):
        self.current_player = 'b' if self.current_player == 'w' else 'w'


def convert_from_str(move):
    x, y = move.split(',')
    x = int(x.strip())
    y = int(y.strip())
    return x, y


def start_game():
    game = Game()
    board = game.board
    print(board.to_ascii())
    while not game.passes[1]:
        move = input('{} please place stone: '.format(game.current_player))
        if move == 'p':
            if game.passes[0]:
                game.passes[1] = True
            else:
                game.passes[0] = True
        else:
            x, y = convert_from_str(move)
            pos = board.pos_by_location((x, y))
            rv = board.imagine_position(pos, game.current_player)
            print(rv)
            if rv['suicide']:
                continue
            # TODO imagine zoborist
            friendly_dragons = list(rv['stitched'])
            touched_dragons = set()
            pos.occupy(game.current_player)
            if not friendly_dragons:
                dragon_id = board.create_new_dragon()
                board.dragons[dragon_id].add_member(pos)
                print(dragon_id)
                touched_dragons.add(board.dragons[dragon_id])
            else:
                base_dragon = friendly_dragons[0]
                base_dragon.add_member(pos)
                for dragon in friendly_dragons[1:]:
                    board.stitch_dragons(base_dragon.identifier, dragon.identifier)
                touched_dragons.add(base_dragon)
            if rv['captured']:
                for dragon in rv['captured']:
                    game.captures[game.current_player] += board.capture_dragon(dragon.identifier)

            touched_dragons.update(rv['opp_neighbor'])
            for dragon in touched_dragons:
                dragon.update()
            game.passes[0] = False
        game.switch_player()
        print(board.to_ascii())
        print(game.captures)

    # game.score()


if __name__ == '__main__':
    start_game()
