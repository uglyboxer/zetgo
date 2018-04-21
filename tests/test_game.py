'''
. . x . x
. x . . x
o x x . x
o x o x .
. o o o .

'''

import pytest
from zetgo.game import Game

__author__ = "Cole Howard"
__copyright__ = "Cole Howard"
__license__ = "mit"


def test_game_passes_complete():
    game = Game(5)
    moves = ['0, 2', '2, 0', '0, 4', '3, 0', '1, 1', '1, 2', '1, 4', '1, 3', '4, 1', '2, 1', '4, 2', '2, 4', '2, 3',
             '3, 3', '3, 2', '3, 1', '4, 3', 'p', 'p']
    for move in moves:
        rv = game.move(move)
    assert rv['complete']


def test_game_get_right_empties():
    game = Game(5)
    moves = ['0, 2', '2, 0', '0, 4', '3, 0', '1, 1', '1, 2', '1, 4', '1, 3', '4, 1', '2, 1', '4, 2', '2, 4', '2, 3',
             '3, 3', '3, 2', '3, 1', '4, 3', 'p', 'p']
    for move in moves:
        rv = game.move(move)
    assert rv['complete']
    rv = game.score()
    assert len(rv) == 4

