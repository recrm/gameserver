from udebs.instance import Instance
from abc import abstractmethod, ABC
import copy
import json
from itertools import zip_longest

class Games(ABC):
    def __init__(self):
        self.games = {}
        self.template = self.createTemplate()

    @abstractmethod
    def createTemplate(self):
        raise NotImplementedError

    def createNew(self):
        return copy.copy(self.template)

class Core(Instance):
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
    #                 pState Management                -
    #---------------------------------------------------
    def pState(self):
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

    def to_json(self):
        current = self.pState()
        canon = min(f(current) for f in self.symmetries)
        endstate = self.getStat("result", "result")

        children = {}
        for child in self.results_data[canon]["children"]:
            # create all symetries
            syms = [f(child) for f in self.symmetries]

            # Get value for this symettry set
            value = self.results_data[min(syms)]

            # Add all symmetries that are on the current path.
            for rep in syms:
                if self.stringDistance(current, rep) == 1:
                    children[rep] = value

        return {
            "current": current,
            "value": self.results_data[canon],
            "children": children,
            "endstate": None if endstate == "" else endstate
        }

    #---------------------------------------------------
    #                 Replacement Methods              -
    #---------------------------------------------------
    @property
    def symmetries(self):
        raise NotImplementedError