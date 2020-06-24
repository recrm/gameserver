from abc import ABC

import udebs
import functools
from collections import OrderedDict
import xml.etree.ElementTree as ET
import pathlib
import pickle

from ..games import Games
from . import udebs_config


class ConnectionManager(Games):
    maxsize = None
    win_cond = None
    type = None
    x = None
    y = None
    field = None

    def __init__(self):
        self.book_path = None
        self.start_book = None
        super().__init__()

    def create_template(self):
        self.book_path = pathlib.Path(__file__).parent / "data" / f"{self.type}-book-{self.x}x{self.y}.pkl"

        try:
            with self.book_path.open("rb") as f:
                self.start_book = pickle.load(f)
        except FileNotFoundError:
            self.start_book = {}

        config = modify_config(udebs_config.config, self.x, self.y)
        main_map = udebs.battleStart(config, field=self.field())

        for state in [main_map, main_map.state[0]]:
            state.start_book = self.start_book
            state.maxsize = self.maxsize
            state.win_cond = self.win_cond

        return main_map


def modify_config(config, x, y):
    tree = ET.parse(config)
    root = tree.getroot()

    root.find("map/dim/x").text = str(x)
    root.find("map/dim/y").text = str(y)

    return ET.tostring(root)


def connect4_cache(f, maxsize=2 ** 20):
    storage = OrderedDict()
    empty = (-float("inf"), float("inf"))

    @functools.wraps(f)
    def cache_wrapper(self, alpha, beta, map_, new_storage=None):
        if new_storage is not None:
            nonlocal storage
            storage = new_storage

        key = self.hash(map_)

        a_, b_ = storage.get(key, empty)
        if a_ > alpha:
            alpha = a_

        # Upper bound optimization magic
        upper = (map_.scored - 1) // 2
        if b_ > upper:
            b_ = upper
        # end magic

        if b_ < beta:
            beta = b_

        if alpha >= beta:
            # Note: Alpha and beta may not be the same.
            # Returning either will produce the right answer, but
            # it is unclear which is more effecient.
            if key in storage:
                storage.move_to_end(key)
            return beta

        result = f(self, alpha, beta, map_)
        if result <= alpha:
            storage[key] = (a_, result)
        elif result >= beta:
            storage[key] = (result, b_)
        else:
            storage[key] = (result, result)

        storage.move_to_end(key)
        if storage.__len__() > maxsize:
            storage.popitem(False)

        return result

    return cache_wrapper


class Connection(udebs.State, ABC):
    # ---------------------------------------------------
    #                 Solver Code                      -
    # ---------------------------------------------------
    def result(self, alpha=None, beta=None):
        map_ = self.getMap().copy()

        key = self.hash(map_)
        if key in self.start_book:
            return self.start_book[key]

        map_.playerx = self.getStat("xPlayer", "ACT") >= 2
        map_.scored = len(map_) - self.time
        map_.const = (map_.x - 1) / 2

        computed = None
        if self.value is not None:
            computed = -(map_.scored + 1) // 2
        else:
            # We have to check if we are one turn away from victory
            for player, loc, move in self.legalMoves():
                if udebs_config.win(map_, player[0], loc) >= self.win_cond:
                    computed = (map_.scored + 1) // 2
                    break

        if computed:
            if alpha and computed < alpha:
                return alpha
            elif beta and computed > beta:
                return beta
            return computed

        if not beta:
            beta = (map_.scored - 1) // 2
        if not alpha:
            alpha = -beta

        return self.negamax(alpha, beta, map_)

    def result(self, alpha=-1, beta=1, storage=None):
        assert alpha < beta

        if storage is None:
            storage = OrderedDict()

        map_ = self.getMap()

        key = self.hash(map_)
        if key in self.start_book:
            return self.start_book[key]

        if self.value is None:
            map_ = self.getMap().copy()
            map_.playerx = self.getStat("xPlayer", "ACT") >= 2
            map_.time = self.time
            map_.scored = len(map_) - self.time
            map_.const = (map_.x - 1) / 2

            with udebs.Timer(verbose=False) as t:
                value = self.negamax(alpha, beta, map_, storage)

            if t.total > 5:
                self.start_book[key] = value
        else:
            value = (len(map_) - self.time) // 2

        if value > beta:
            return beta
        if value < alpha:
            return alpha
        return value

    @staticmethod
    def play_next(map_, token, loc):
        new = map_.copy()
        new.playerx = not map_.playerx
        new[loc] = token
        new.time = map_.time + 1
        new.scored = map_.scored - 1
        return new

    def legalMoves2(self, map_):
        raise NotImplementedError

    @connect4_cache
    def negamax(self, alpha, beta, map_):
        current = -float("inf")
        for move in self.legalMoves2(map_):
            try:
                token, loc = move
            except TypeError:
                computed = -move
            else:
                computed = -self.negamax(-beta, -alpha, self.play_next(map_, token, loc))

            if computed > current:
                current = computed
                if computed > alpha:
                    alpha = computed
                    if alpha >= beta:
                        break

        return current

    # ---------------------------------------------------
    #                   hash Management                -
    # ---------------------------------------------------
    def __str__(self):
        map_ = self.getMap()
        buf = ''
        for y in range(map_.y):
            for x in range(map_.x):
                entry = map_[x, y]
                if entry == "empty":
                    entry = "_"
                buf += entry[0]
            buf += "|"

        return buf.rstrip("|")

    def to_json(self, solver=True):
        storage = OrderedDict()

        if self.value is None and solver:
            children = {str(i): -i.result(-1, 1, storage) for i, e in self.substates()}
        else:
            children = {}

        return {
            "current": str(self),
            "children": children,
            "endstate": self.value
        }
