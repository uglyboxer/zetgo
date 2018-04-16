class Board(object):

    def __init__(self, board_size):
        self.board_size = board_size
        self.dragons = {}
        self.positions = [[Position(x, y, self.board_size) for y in range(self.board_size)] for x in range(self.board_size)]

    @property
    def next_dragon(self):
        if not self.dragons:
            return 1
        return max(self.dragons.keys()) + 1

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

    def get_neighboring_dragons(self, pos, color):
        neighbors = [self.pos_by_location(x) for x in pos.neighbors_locs]
        rv = set()
        for x in neighbors:
            if x.dragon and x.color == color:
                rv.add(self.dragons[x.dragon])
        return rv

    def get_opposing_color(self, color):
        if not color:
            return None
        elif color == 'b':
            return 'w'
        return 'b'

    def imagine_position(self, pos, color):
        """
        For a given position instance, imagine the outcome playing there.

        Args:
            pos Position instance
            color str: 'b' or 'w'
        Returns:
            dict  {'suicide': bool,
                   'captured': list of dragon instances,
                   'stitched': list of dragon instances}
        """
        rv = {'suicide': False,
              'captured': set(),
              'opp_neighbor': set(),
              'stitched': set()}
        opposing_dragons = self.get_neighboring_dragons(pos, self.get_opposing_color(color))
        self_dragons = self.get_neighboring_dragons(pos, color)
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
        elif not rv['captured'] or not check_for_suicide:
            rv['suicide'] = True
        else:
            raise NotImplementedError('Must be liberties or resulting captures.  Should not be able to get here.')

        return rv

    def imagine_stitched_valid(self, pos, dragons):
        """
        Checks to see if the current position is the last liberty of all associated dragons
        """
        if not dragons:
            return False
        liberties = set()
        for dragon in dragons:
            print('liberties: {}'.format(dragon.liberties))
            liberties.update(dragon.liberties)
        if liberties == {pos}:
            return False
        return True

    def capture_dragon(self, dragon_id):
        d = self.dragons[dragon_id]
        captures = len(d.members)
        for pos in d.members:
            pos.color = None
            pos.dragon = None
        del self.dragons[dragon_id]
        del d
        return captures

    def to_ascii(self):
        board = ''
        for row in self.positions:
            r = ''
            for pos in row:
                if pos.color == 'b':
                    color = 'x '
                elif pos.color == 'w':
                    color = 'o '
                else:
                    color = '. '
                r += color
            r += '\n'
            board += r
        return board


class Position(object):

    def __init__(self, x, y, board_size):
        self.x = x
        self.y = y
        self.board_size = board_size

        self.dragon = None
        self.color = None
        self.neighbors_locs = self.init_neighbors()

    @property
    def loc(self):
        return (self.x, self.y)

    @property
    def is_occupied(self):
        return self.color is not None

    @property
    def opposing_color(self):
        if not self.color:
            return None
        elif self.color == 'b':
            return 'w'
        return 'b'

    def occupy(self, color):
        self.color = color

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
        self.color = None
        self.board = board
        self.members = set()
        self.neighbors = set()
        self.liberties = set()

    def is_member(self, pos):
        return pos in self.members

    def update(self):
        self.liberties = set([x for x in self.neighbors if not x.is_occupied])

    def add_member(self, pos, force=False):
        if self.color and self.color != pos.color:
            raise NotImplementedError('Wrong color to connect to this dragon.')

        if not force and self.members and pos not in self.neighbors:
            raise NotImplementedError('Cannot connect to this dragon.')

        if not self.color:
            self.color = pos.color
        pos.dragon = self.identifier
        self.members.add(pos)
        self.neighbors.update(set([self.board.pos_by_location(x) for x in pos.neighbors_locs]))
        self.neighbors = self.neighbors - self.members
        self.liberties = {x for x in self.neighbors if not x.is_occupied}
