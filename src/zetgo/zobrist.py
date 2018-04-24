'''
adpated from TictactoeZobrist by https://github.com/blackicetee
'''
from random import SystemRandom


class Zobrist:
    def __init__(self, board_size):
        secure_random = SystemRandom()
        self.zArray = [[secure_random.randrange(1000000000), secure_random.randrange(1000000000)] for i in range(board_size ** 2)]

    def get_zobrist_board_position_array(self):
        return self.zArray

    def set_zobrist_board_position_array(self, zobrist_board_position_array):
        self.zArray = zobrist_board_position_array

    def get_hash(self, _game_matrix, fake=False):
        zobrist_key = 0
        _game_fields = self.transform_game_matrix_to_one_dimensional_list(_game_matrix, fake=fake)
        for i in range(len(_game_fields)):
            if _game_fields[i] == 1:
                zobrist_key ^= self.zArray[i][0]
            elif _game_fields[i] == -1:
                zobrist_key ^= self.zArray[i][1]
        return zobrist_key

    def transform_game_matrix_to_one_dimensional_list(self, _game_matrix, fake=False):
        one_dimensional_list = []
        for row in _game_matrix:
            for col in row:
                if fake:
                    one_dimensional_list.append(col)
                else:
                    one_dimensional_list.append(col.player)
        return one_dimensional_list
