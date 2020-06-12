import udebs
import functools
from itertools import zip_longest
from collections import OrderedDict
import xml.etree.ElementTree as ET
import pathlib
import pickle

from ..games import Games
from . import udebs_config

class ConnectionManager(Games):
    def createTemplate(self):
        self.path = pathlib.Path(__file__).parent / "data" / f"{self.type}-{self.x}x{self.y}.pkl"
        self.book_path = pathlib.Path(__file__).parent / "data" / f"{self.type}-book-{self.x}x{self.y}.pkl"

        try:
            with (self.path).open("rb") as f:
                self.storage = pickle.load(f)
        except FileNotFoundError:
            self.storage = OrderedDict()

        try:
            with (self.book_path).open("rb") as f:
                self.start_book = pickle.load(f)
        except FileNotFoundError:
            self.start_book = {}

        config = modifyconfig(udebs_config.config, self.x, self.y)
        main_map = udebs.battleStart(config, field=self.field())

        for state in [main_map, main_map.state[0]]:
            state.storage = self.storage
            state.start_book = self.start_book
            state.maxsize = self.maxsize
            state.win_cond = self.win_cond

        return main_map

def modifyconfig(config, x, y):
    tree = ET.parse(config)
    root = tree.getroot()

    root.find("map/dim/x").text = str(x)
    root.find("map/dim/y").text = str(y)

    return ET.tostring(root)

def connect4_cache(f, maxsize=2**20):
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

        if b_ < beta:
            beta = b_

        if alpha >= beta:
            # Note: Alpha and beta may not be the same.
            # Returning either will produce the right answer, but
            # it is unclear which is more effecient.
            return beta

        result = f(self, alpha, beta, map_)
        if result <= alpha:
            storage[key] = (a_, result)
        elif result >= beta:
            storage[key] = (result, b_)
        else:
            storage[key] = (result, result)

        storage.move_to_end(key)
        while storage.__len__() > maxsize:
            storage.popitem(False)

        return result
    return cache_wrapper

class Connection(udebs.State):
    #---------------------------------------------------
    #                 Solver Code                      -
    #---------------------------------------------------
    def result(self, alpha=-1, beta=1):
        assert alpha < beta

        map_ = self.getMap()

        key = self.hash(map_)
        if key in self.start_book:
            return self.start_book[key]

        if self.value is None:
            map_ = self.getMap().copy()
            map_.playerx = self.getStat("xPlayer", "ACT") >= 2
            map_.time = self.time

            with udebs.Timer(verbose=False) as t:
                value = self.negamax(alpha, beta, map_, self.storage)

            if t.total > 5:
                self.start_book[key] = value
        else:
            value = -int((len(map_) - self.time) / 2)

        if value > beta:
            return beta
        if value < alpha:
            return alpha
        return value

    def substates2(self, map_):
        for move in self.legalMoves2(map_):
            if not isinstance(move, tuple):
                yield move, move
            else:
                stateNew = map_.copy()
                stateNew.playerx = not map_.playerx
                stateNew[move[1]] = move[0]
                stateNew.time = map_.time + 1
                yield stateNew, move

    @connect4_cache
    def negamax(self, alpha, beta, map_):
        for child, e in self.substates2(map_):
            if child is e:
                result = -child
            else:
                result = -self.negamax(-beta, -alpha, child)

            if result > alpha:
                alpha = result
                if alpha >= beta:
                    return alpha

        return alpha

    #---------------------------------------------------
    #                   hash Management                -
    #---------------------------------------------------
    def __str__(self):
        map_ = self.getMap()
        buf = ''
        for y in range(map_.y):
            for x in range(map_.x):
                entry = map_[x,y]
                if entry == "empty":
                    entry = "_"
                buf += entry[0]
            buf += "|"

        return buf.rstrip("|")

    def to_json(self, solver=True):
        if self.value is None and solver:
            children = {str(i): -i.result() for i,e in self.substates()}
        else:
            children = {}

        return {
            "current": str(self),
            "children": children,
            "endstate": self.value
        }
