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

            key = hash(self)
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
                        new = f(self, -value[2], -value[1], **kwargs)
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

    #---------------------------------------------------
    #                 Main Symmetries                  -
    #---------------------------------------------------
    @staticmethod
    def symmetry_x(split):
        split = split.split("|")
        return "|".join(i[::-1] for i in split)

    @staticmethod
    def symmetry_y(split):
        split = split.split("|")
        return "|".join(reversed(split))

    @staticmethod
    def symmetry_90(split):
        split = split.split("|")
        return "|".join("".join(x) for x in zip(*split))

    @staticmethod
    def symmetry_180(split):
        split = split.split("|")
        return "|".join(reversed([i[::-1] for i in split]))

    @staticmethod
    def symmetry_270(split):
        split = split.split("|")
        new = reversed([i[::-1] for i in split])
        return "|".join("".join(x) for x in zip(*new))

    @staticmethod
    def identity(split):
        return split

    @staticmethod
    def stringDistance(one, two):
        count = 0
        for x, y in zip_longest(one, two):
            if x != y:
                count +=1
        return count

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

    def result(self):
        endstate = self.endState()
        if endstate is not None:
            return -abs(endstate)

        clone = self.modifystate()
        return clone.negamax(-1, 1, storage=self.storage, maxsize=self.maxsize, verbose=False)

    @udebs.countrecursion
    @connect4_cache
    def negamax(self, alpha=-1, beta=1):
        value = -float("inf")
        for child, e in self.substates():
            result = child
            if child is not e:
                result = -child.negamax(-beta, -alpha)

            if result > value:
                value = result
                if result > alpha:
                    alpha = result

            if alpha >= beta:
                return value

        return value

    #---------------------------------------------------
    #                 pState Management                -
    #---------------------------------------------------
    def __hash__(self):
        rState = str(self)
        canon = min(f(rState) for f in self.symmetries)

        buf = ""
        for char in canon:
            if char == "_":
                buf += "0"
            elif char == "x":
                buf += "1"
            elif char == "o":
                buf += "2"
            elif char == "|":
                continue
            else:
                raise TypeError("unknown character", char)

        return int(buf, 3)

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
        endstate = self.endState()

        if endstate is None and solver:
            children = {str(i): -i.result() for i,e in self.substates(self.fullChildren())}
        else:
            children = {}

        return {
            "current": str(self),
            "children": children,
            "endstate": endstate
        }

    #---------------------------------------------------
    #                 Replacement Methods              -
    #---------------------------------------------------
    @property
    def symmetries(self):
        raise NotImplementedError
