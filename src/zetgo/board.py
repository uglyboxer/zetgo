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

    def get_neighboring_dragons(self, pos, player):
        neighbors = [self.pos_by_location(x) for x in pos.neighbors_locs]
        rv = set()
        for x in neighbors:
            if x.dragon and x.player == player:
                rv.add(self.dragons[x.dragon])
        return rv

    def get_opposing_player(self, player):
        if not player:
            return 0
        elif player == 1:
            return -1
        return 1

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
              'captured': set(),
              'opp_neighbor': set(),
              'stitched': set()}
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

        rv = {}
        empty = []
        empty_ds = set()
        for x in range(self.board_size):
            for y in range(self.board_size):
                if not self.positions[x][y].is_occupied:
                    empty.append(self.positions[x][y])

        for pos1 in empty:
            if not pos1.dragon:  #TODO this creates secondary dragons sometimes.  Need to catch or stitch
                dragon_id = self.create_new_dragon()
                dragon = self.dragons[dragon_id]
                empty_ds.add(dragon)
                dragon.add_member(pos1)
            else:
                dragon = self.dragons[pos1.dragon]

            for pos2 in empty:
                if pos1 == pos2:
                    continue
                if pos2 in dragon.neighbors:
                    dragon.add_member(pos2)

        pairs_to_stitch = []
        for d in empty_ds:
            for x in empty_ds:
                if d == x:
                    continue
                if d.neighbors.intersection(x.members):
                    pairs_to_stitch.append((d.identifier, x.identifier))

        for p, q in pairs_to_stitch:
            self.stitch_dragons(p, q)

        for d in empty_ds:
            surr_color = set()
            for x in d.neighbors:
                surr_color.add(x.player)
            if len(surr_color) == 1:
                rv[list(surr_color)[0]].add(d)
                print('{} surrounded by {}'.format(d.identifier, surr_color))
        return empty_ds

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
