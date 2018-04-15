#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from zetgo.board import Board, Position, Dragon

__author__ = "Cole Howard"
__copyright__ = "Cole Howard"
__license__ = "mit"


@pytest.fixture
def board():
    board_size = 19
    return Board(board_size)


# ===== Board ========

def test_board_size(board):

    assert len(board.positions) == 19
    assert len(board.positions[0]) == 19


def test_stitch_dragons(board):
    board.dragons[1] = Dragon(1, board)
    board.dragons[2] = Dragon(2, board)
    for x in range(3):
        p = board.pos_by_location((1, 1 + x))
        p.color = 'b'
        board.dragons[1].add_member(p)
        q = board.pos_by_location((3, 1 + x))
        q.color = 'b'
        board.dragons[2].add_member(q)
    r = board.pos_by_location((2, 1))
    r.color = 'b'
    board.dragons[1].add_member(r)

    assert len(board.dragons) == 2
    board.stitch_dragons(1, 2)
    assert len(board.dragons) == 1
    with pytest.raises(KeyError):
        assert board.dragons[2]


def test_stitch_unconnected_dragons(board):
    board.dragons[1] = Dragon(1, board)
    board.dragons[2] = Dragon(2, board)
    for x in range(3):
        p = board.pos_by_location((1, 1 + x))
        board.dragons[1].add_member(p)
        q = board.pos_by_location((3, 1 + x))
        board.dragons[2].add_member(q)

    assert len(board.dragons) == 2
    with pytest.raises(NotImplementedError):
        board.stitch_dragons(1, 2)


def test_get_neighboring_dragons(board):
    pass


def test_capture_dragon(board):
    d = Dragon(1, board)
    board.dragons[1] = d
    for x in range(4):
        p = board.positions[3][2+x]
        p.color = 'b'
        p.dragon = 1
        d.add_member(p)

    p = board.positions[4][5]
    p.color = 'b'
    p.dragon = 1
    d.add_member(p)
    rv = board.capture_dragon(1)
    assert rv == 5


def test_to_ascii(board):
    pass


# ===== Position ========

def test_position_attributes():
    p = Position(2, 3, 19)
    assert p.is_occupied is False
    assert p.color is None
    assert p.neighbors_locs == set([(1, 3), (3, 3), (2, 2), (2, 4)])

    p2 = Position(0, 2, 19)
    assert p2.neighbors_locs == set([(1, 2), (0, 1), (0, 3)])


def test_position_occupy():
    p = Position(0, 2, 19)
    assert p.color is None
    assert p.is_occupied is False
    p.occupy('b')
    assert p.color == 'b'
    assert p.is_occupied is True


def test_opposing_color():
    p = Position(0, 2, 19)
    assert p.color is None
    assert p.opposing_color is None
    p.occupy('b')
    assert p.opposing_color == 'w'

    p = Position(9, 4, 19)
    assert p.color is None
    assert p.opposing_color is None
    p.occupy('w')
    assert p.opposing_color == 'b'


# ===== Dragon ========

def test_is_member(board):
    d = Dragon(1, board)
    p = board.positions[1][2]
    assert not d.is_member(p)

    d.add_member(p)
    assert d.is_member(p)


def test_neighbors(board):
    d = Dragon(1, board)
    p = board.positions[1][2]
    p2 = board.positions[1][3]
    d.add_member(p2)
    d.add_member(p)

    assert len(d.neighbors) == 6
    assert len(d.members) == 2
    assert d.liberties == 6


def test_edge_neighbors(board):
    d = Dragon(1, board)
    p = board.positions[18][2]
    p2 = board.positions[18][3]
    d.add_member(p2)
    d.add_member(p)

    assert len(d.neighbors) == 4
    assert len(d.members) == 2
    assert d.liberties == 4
