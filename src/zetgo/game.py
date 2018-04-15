from board import Board


class Game:

    def __init__(self, board_size=19, *args, **kwargs):
        self.black_player = None
        self.white_plater = None
        self.board = Board(board_size=board_size)
        self.current_player = None

