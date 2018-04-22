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


@pytest.fixture()
def game():
    return Game(5)


@pytest.fixture()
def moves():
    return ['0, 2', '0, 3', '0, 4', '1, 2', '1, 1', '1, 3', '1, 4', '2, 0', '2, 1', '2, 3', '2, 2', '3, 0', '2, 4',
            '3, 2', '3, 1', '4, 2', '4, 1', '4, 3', '3, 3', 'p', 'p']


def test_pass_resets(game):
    rv = game.move('1, 1')
    assert not rv['complete']
    rv = game.move('p')
    assert not rv['complete']
    rv = game.move('2, 1')
    assert not rv['complete']
    rv = game.move('3, 1')
    assert not rv['complete']
    rv = game.move('p')
    assert not rv['complete']
    rv = game.move('1, 4')
    assert not rv['complete']
    rv = game.move('p')
    assert not rv['complete']
    rv = game.move('p')
    assert rv['complete']


def test_game_passes_complete(game, moves):
    for move in moves:
        rv = game.move(move)
    assert rv['complete']


def test_game_get_right_empties(game, moves):
    for move in moves:
        rv = game.move(move)
    assert rv['complete']
    print(game.board.to_ascii())
    rv = game.board.set_empty_dragons()
    assert len(rv['all_dragons']) == 4
    assert not rv[-1]
    assert len(rv[1]) == 1


def test_score(game, moves):
    for move in moves:
        rv = game.move(move)
    rv = game.score()
    assert rv == {1: 8, -1: 0}
