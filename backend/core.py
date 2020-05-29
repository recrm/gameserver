from udebs.treesearch import State
from abc import abstractmethod, ABC
import copy
from itertools import zip_longest
from expiringdict import ExpiringDict

class Games(ABC):
    def __init__(self):
        self.games = ExpiringDict(max_len=50, max_age_seconds=3600)
        self.template = self.createTemplate()

    @abstractmethod
    def createTemplate(self):
        raise NotImplementedError

    def createNew(self):
        return copy.copy(self.template)

class Core(State):
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

    def results_data(self, value):
        return NotImplementedError

    #---------------------------------------------------
    #                 pState Management                -
    #---------------------------------------------------
    def __str__(self):
        rState = self.rState()
        return min(f(rState) for f in self.symmetries)

    def rState(self):
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
        endstate = self.endState()
        if endstate is None:
            children = {i.rState(): -i.results_data() for i,e in self.substates(self.fullChildren())}
        else:
            children = {}

        return {
            "current": self.rState(),
            "value": self.results_data(),
            "children": children,
            "endstate": endstate
        }

    #---------------------------------------------------
    #                 Replacement Methods              -
    #---------------------------------------------------
    @property
    def symmetries(self):
        raise NotImplementedError
