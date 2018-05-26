from collections import deque

import numpy as np

from zetgo.zobrist import Zobrist


class Board(object):

    def __init__(self, board_size, state=None, current_player=None):
        self.board_size = board_size
        self.dragons = {}
        self.positions = [[Position(x, y, self.board_size) for y in range(self.board_size)] for x in range(self.board_size)]
        self.zobrist = Zobrist(self.board_size)
        self.z_table = set()
        self.current_player = current_player or 1
        self.captures = {1: 0, -1: 0}
        self.passes = [False, False]
        self.history = deque([], maxlen=7)
        if state:
            self._generate_from_state(state)

    @property
    def next_dragon(self):
        if not self.dragons:
            return 1
        return max(self.dragons.keys()) + 1

    def switch_player(self):
        self.current_player = self.current_player * -1

    def _generate_from_state(self, state):
        '''
        Assumes only valid histories passed in as state.  Otherwise False returns
        from the act method would be treated as a pass.  Not ideal, but okay
        until refactor time.

        Args:
            state  np.array  stack of 7 board positions 1's for b, -1's for w,
                                      1 layer for current player TO PLAY
        '''
        self.current_player = state[7][0]
        for idx, row in enumerate(state[0]):
            for idy, player_val in enumerate(row):
                # TODO does it matter if this is out of order?
                if player_val == 0:
                    continue
                rv = self.act((idx, idy), player_val)

        for ts in state[:7]:
            zhash = self.zobrist.get_hash(ts)
            self.z_table.add(zhash)

    def dump_state_example(self):
        current = np.ones((self.board_size, self.board_size)) * self.current_player
        history = list(self.history)
        history.append(current)
        return np.stack(history)

    def update_history(self):
        state = []
        for row in self.positions:
            row_vals = []
            for pos in row:
                row_vals.append(pos.player)
            state.append(row_vals)

        self.history.append(np.array(state))

    def act(self, loc):
        result = {'complete': False,
                  'valid': True,
                  'captures': {1: 0, -1: 0}}
        pos = self.pos_by_location(loc)
        rv = self.imagine_position(pos, self.current_player)
        if rv['occupied'] or rv['suicide'] or rv['repeat']:
            result['valid'] = False
            return result
        friendly_dragons = list(rv['stitched'])
        touched_dragons = set()
        pos.occupy(self.current_player)
        if not friendly_dragons:
            dragon_id = self.create_new_dragon()
            self.dragons[dragon_id].add_member(pos)
            touched_dragons.add(self.dragons[dragon_id])
        else:
            base_dragon = friendly_dragons[0]
            base_dragon.add_member(pos)
            for dragon in friendly_dragons[1:]:
                self.stitch_dragons(base_dragon.identifier, dragon.identifier)
            touched_dragons.add(base_dragon)
        if rv['captured']:
            for dragon in rv['captured']:
                result['captures'][self.current_player] += self.capture_dragon(dragon.identifier)

        touched_dragons.update(rv['opp_neighbor'])
        for dragon in touched_dragons:
            dragon.update()

        self.z_table.add(rv['zhash'])
        self.update_history()
        return result

    def take_action(self, loc):
        """ Wrapper for act for DRL to use """
        done = False
        result = self.act(loc)
        if result['complete']:
            winner = self.score()
            if winner == self.current_player:
                value = 1
            else:
                value = 0
            done = True
        return self, value, done

    def add_up_score(self, player, dragons):
        for d in dragons:
            self.captures[player] += len(d.members)

    def score(self):
        rv = self.set_empty_dragons()
        for x in [-1, 1]:
            self.add_up_score(x, rv[x])
        caps = [self.captures[-1], -100000, self.captures[1]]
        return caps.index(max(caps)) - 1  # Okay this is embarassing hack.  sorry

    def allowed_plays(self, for_player):
        allowed = []
        open_pos = []

        for row in self.positions:
            for pos in row:
                if not pos.is_occupied:
                    open_pos.append(pos)
        for pos in open_pos:
            rv = self.imagine_position(pos, for_player)
            if rv['suicide'] or rv['repeat']:
                continue
            allowed.append(pos.loc)
        return allowed

    def imagine_zobrist(self, pos, captures, player):
        board = self.fake_board(pos, captures, player)
        return self.zobrist.get_hash(board, fake=True)

    def create_new_dragon(self):
        dragon_id = self.next_dragon
        self.dragons[dragon_id] = Dragon(dragon_id, self)
        return dragon_id

    def pos_by_location(self, tup):
        '''
        Get instance at position from a tuple index

        Args: tup  (int, int)

        Return:
            Position instance
        '''
        x = tup[0]
        y = tup[1]
        if x < 0 or x > self.board_size or y < 0 or y > self.board_size:
            raise NotImplementedError('Tuple outside of board size of {}'.format(self.board_size))

        return self.positions[x][y]

    def stitch_dragons(self, d1_id, d2_id):
        """
        Stitch two dragons into one.
        Args:
            d1, d2  2 keys to the dragon dictionary

        Return:
            Dragon instance
        """
        d1 = self.dragons[d1_id]
        d2 = self.dragons[d2_id]

        if not d1.neighbors.intersection(d2.members):
            raise NotImplementedError('Cannot merge unconnected dragons.')
        for member in d2.members:
            d1.add_member(member, force=True)
        del self.dragons[d2_id]
        del d2
        return d1

    def get_neighboring_dragons(self, pos, player):
        neighbors = [self.pos_by_location(x) for x in pos.neighbors_locs]
        rv = set()
        for x in neighbors:
            if x.dragon and x.player == player:
                rv.add(self.dragons[x.dragon])
        if player == 0:
            print(rv)
        return rv

    def get_opposing_player(self, player):
        if not player:
            return 0
        elif player == 1:
            return -1
        return 1

    def fake_board(self, pos, captures, player):
        fake = []
        for row in self.positions:
            fake_row = []
            for point in row:
                fake_row.append(point.player)
            fake.append(fake_row)
        fake[pos.x][pos.y] = player

        for captured_dragon in captures:
            for capture in captured_dragon.members:
                fake[capture.x][capture.y] = 0
        return fake

    def imagine_position(self, pos, player):
        """
        For a given position instance, imagine the outcome playing there.

        Args:
            pos Position instance
            player str: 1 or -1
        Returns:
            dict  {'suicide': bool,
                   'captured': list of dragon instances,
                   'stitched': list of dragon instances}
        """
        rv = {'suicide': False,
              'occupied': False,
              'repeat': False,
              'zhash': None,
              'captured': set(),
              'opp_neighbor': set(),
              'stitched': set()}
        if pos.is_occupied:
            rv['occupied'] = True
            return rv

        opposing_dragons = self.get_neighboring_dragons(pos, self.get_opposing_player(player))
        self_dragons = self.get_neighboring_dragons(pos, player)
        neighbors = [self.pos_by_location(x) for x in pos.neighbors_locs]
        liberties = [x for x in neighbors if not x.is_occupied]

        for opp_dragon in opposing_dragons:
            if opp_dragon.liberties == {pos}:
                rv['captured'].add(opp_dragon)
            else:
                rv['opp_neighbor'].add(opp_dragon)

        check_for_suicide = self.imagine_stitched_valid(pos, self_dragons)

        if liberties or check_for_suicide:
            rv['stitched'] = self_dragons
        elif not liberties and not rv['captured']:
            rv['suicide'] = True

        rv['zhash'] = self.imagine_zobrist(pos, rv['captured'], player)
        if rv['zhash'] in self.z_table:
            rv['repeat'] = True
        return rv

    def imagine_stitched_valid(self, pos, dragons):
        """
        Checks to see if the current position is the last liberty of all associated dragons
        """
        if not dragons:
            return False
        liberties = set()
        for dragon in dragons:
            liberties.update(dragon.liberties)
        if liberties == {pos}:
            return False
        return True

    def capture_dragon(self, dragon_id):
        d = self.dragons[dragon_id]
        captures = len(d.members)
        opposing_dragons = set()
        for pos in d.members:
            opposing_dragons.update(self.get_neighboring_dragons(pos, self.get_opposing_player(d.player)))

            pos.player = 0
            pos.dragon = None
        for dragon in opposing_dragons:
            dragon.update()
        del self.dragons[dragon_id]
        del d
        return captures

    def set_empty_dragons(self):

        rv = {'all_dragons': set(),
              1: set(),
              -1: set()}
        empty = []
        for x in range(self.board_size):
            for y in range(self.board_size):
                if not self.positions[x][y].is_occupied:
                    empty.append(self.positions[x][y])
        for pos1 in empty:
            if not pos1.dragon:
                n_dragons = list(self.get_neighboring_dragons(pos1, 0))
                if n_dragons:
                    d1 = n_dragons[0]
                    d1.add_member(pos1)
                    rv['all_dragons'].add(d1.identifier)
                    for d in n_dragons[1:]:
                        self.stitch_dragons(d1.identifier, d.identifier)
                else:
                    dragon_id = self.create_new_dragon()
                    dragon = self.dragons[dragon_id]
                    rv['all_dragons'].add(dragon.identifier)
                    dragon.add_member(pos1)
            else:
                dragon = self.dragons[pos1.dragon]
            for pos2 in empty:
                if pos1 == pos2:
                    continue
                if pos2 in dragon.neighbors:
                    dragon.add_member(pos2)

        for d_id in rv['all_dragons']:
            d = self.dragons[d_id]
            surr_color = set()
            for x in d.neighbors:
                surr_color.add(x.player)
            if len(surr_color) == 1:
                rv[list(surr_color)[0]].add(d)
        return rv

    def to_ascii(self):
        board = ''
        for row in self.positions:
            r = ''
            for pos in row:
                if pos.player == 1:
                    player = 'x '
                elif pos.player == -1:
                    player = 'o '
                else:
                    player = '. '
                r += player
            r += '\n'
            board += r
        return board


class Position(object):

    def __init__(self, x, y, board_size):
        self.x = x
        self.y = y
        self.board_size = board_size

        self.dragon = None
        self.player = 0
        self.neighbors_locs = self.init_neighbors()

    def __str__(self):
        return '{}, {}'.format(self.x, self.y)

    @property
    def loc(self):
        return (self.x, self.y)

    @property
    def is_occupied(self):
        return self.player != 0

    @property
    def opposing_player(self):
        if not self.player:
            return 0
        elif self.player == 1:
            return -1
        return 1

    def occupy(self, player):
        self.player = player

    def init_neighbors(self):

        neighbors = []
        possible = [(self.x - 1, self.y), (self.x + 1, self.y), (self.x, self.y - 1), (self.x, self.y + 1)]
        for x, y in possible:
            if x >= 0 and x < self.board_size and y >= 0 and y < self.board_size:
                neighbors.append((x, y))
        return set([(x, y) for x, y in neighbors])


class Dragon(object):

    def __init__(self, identifier, board):

        self.identifier = identifier
        self.player = 0
        self.board = board
        self.members = set()
        self.neighbors = set()
        self.liberties = set()

    def is_member(self, pos):
        return pos in self.members

    def update(self):
        self.liberties = set([x for x in self.neighbors if not x.is_occupied])

    def add_member(self, pos, force=False):
        if self.player and self.player != pos.player:
            raise NotImplementedError('Wrong player to connect to this dragon.')

        if not force and self.members and pos not in self.neighbors:
            raise NotImplementedError('Cannot connect to this dragon.')

        if not self.player:
            self.player = pos.player
        pos.dragon = self.identifier
        self.members.add(pos)
        self.neighbors.update(set([self.board.pos_by_location(x) for x in pos.neighbors_locs]))
        self.neighbors = self.neighbors - self.members
        self.liberties = {x for x in self.neighbors if not x.is_occupied}
