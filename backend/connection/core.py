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

        try:
            with (self.path).open("rb") as f:
                self.storage = pickle.load(f)
        except FileNotFoundError:
            self.storage = OrderedDict()

        config = modifyconfig(udebs_config.config, self.x, self.y)
        main_map = udebs.battleStart(config, field=self.field())

        for state in [main_map, main_map.state[0]]:
            state.storage = self.storage
            state.maxsize = self.maxsize
            state.win_cond = self.win_cond

        return main_map

def modifyconfig(config, x, y):
    tree = ET.parse(config)
    root = tree.getroot()

    root.find("map/dim/x").text = str(x)
    root.find("map/dim/y").text = str(y)

    return ET.tostring(root)

def connect4_cache(f=None, maxsize=None, storage=None):
    if maxsize is None:
        maxsize = 2**20

    if storage is None:
        storage = OrderedDict()

    def cache(f):
        @functools.wraps(f)
        def wrapper(self, alpha, beta, **kwargs):
            if "storage" in kwargs:
                nonlocal storage
                storage = kwargs.pop("storage")

            if "maxsize" in kwargs:
                nonlocal maxsize
                maxsize = kwargs.pop("maxsize")

            key = self.hash()
            value = storage.get(key, None)
            if value is not None:
                try:
                    value[1]
                except TypeError:
                    return value
                else:
                    if value[1] == alpha and value[2] == beta:
                        storage.move_to_end(key)
                        return value[0]
                    else:
                        new = f(self, -value[2], -value[1])
                        storage[key] = new
                        storage.move_to_end(key)
                        return new

            value = f(self, alpha, beta, **kwargs)
            if value != 0 or alpha + beta == 0:
                storage[key] = value
            else:
                storage[key] = (value, alpha, beta)

            while (storage.__len__() > maxsize):
                storage.popitem(False)

            return value

        return wrapper

    return cache if f is None else cache(f)

class Connection(udebs.State):
    storage = OrderedDict()
    maxsize = 2**17

    @staticmethod
    def identity(split):
        return split

    #---------------------------------------------------
    #                 Solver Code                      -
    #---------------------------------------------------
    def modifystate(self):
        return udebs.modifystate(self, {
            "drop": {"group": []},
            "placement": {"group": []},
            "xPlayer": {"immutable": True},
            "oPlayer": {"immutable": True},
        })

    def result(self, alpha=-1, beta=1, storage=None, maxsize=None):
        if self.value is not None:
            return -abs(self.value)

        if storage is None:
            storage = self.storage

        if maxsize is None:
            maxsize = self.maxsize

        clone = self.modifystate()
        return clone.negamax(alpha, beta, storage=storage, maxsize=maxsize)

    @connect4_cache
    def negamax(self, alpha=-float("inf"), beta=float("inf")):
        value = -float("inf")
        for child, e in self.substates():
            if child is e:
                result = -child
            else:
                result = -child.negamax(-beta, -alpha)

            if result > value:
                value = result
                if value > alpha:
                    alpha = value

            if alpha >= beta:
                break

        return value

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
            children = {str(i): -i.result() for i,e in self.substates(self.fullChildren())}
        else:
            children = {}

        return {
            "current": str(self),
            "children": children,
            "endstate": self.value
        }
