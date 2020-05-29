import pathlib
import functools
import pickle
import xml.etree.ElementTree as ET
from collections import OrderedDict

import udebs

from ..core import Core, Games
from . import udebs_config

def connect4_cache(f=None, maxsize=None, storage=None):
    if maxsize is None:
        maxsize = 2**23

    if storage is None:
        storage = OrderedDict()

    def cache(f):
        @functools.wraps(f)
        def wrapper(self, alpha, beta, **kwargs):
            if "storage" in kwargs:
                nonlocal storage
                storage = kwargs.pop("storage")

            key = self.pState()
            value = storage.get(key, None)
            if value is not None:
                try:
                    if value[1] == alpha and value[2] == beta:
                        storage.move_to_end(key)
                        return value[0]
                    else:
                        new = f(self, -value[2], -value[1], **kwargs)
                        storage[key] = new
                        storage.move_to_end(key)
                        return new
                except TypeError:
                    return value

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

class Connect4_core(Core):
    def results_data(self):
        endstate = self.endState()
        if endstate is not None:
            return -abs(endstate)

        clone = udebs.modifystate(self, {
            "drop": {"group": []},
            "xPlayer": {"immutable": True},
            "oPlayer": {"immutable": True},
        })

        return clone.negamax(-1, 1, storage=self.data_storage, verbose=False)

    def fullChildren(self):
        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        for x in range(self.map["map"].x):
            yield player, (x, 0), "drop"

    def legalMoves(self):
        map_ = self.map["map"]

        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        other = self.getStat("oPlayer" if player == "xPlayer" else "xPlayer", "token")
        token = self.getStat(player, "token")

        options = []
        forced = None
        backup = None

        for x in range(map_.x):
            y = udebs_config.BOTTOM(map_, x)
            if y is not None:
                loc = (x,y)
                position = player, loc, "drop"

                # First check if we win here.
                if udebs_config.win(map_, token, loc) >= 4:
                    yield 1
                    return

                # we are in check, must play here
                elif udebs_config.win(map_, other, loc) >= 4:
                    if forced is None:
                        forced = position
                    else:
                        yield -1
                        return

                elif forced is None:
                    # This would put us in check, can't play here
                    if y > 0 and udebs_config.win(map_, other, (x, y - 1)) >= 4:
                        backup = position

                    else:
                        options.append((
                            *position,
                            udebs_config.win(map_, token, loc), -abs(((map_.x - 1) / 2) - x)
                        ))

        if forced is not None:
            yield forced
        elif len(options) == 0:
            yield backup if backup is not None else 0
        else:
            yield from sorted(options, key=lambda x: x[3:5], reverse=True)

    @property
    def symmetries(self):
        return [self.identity, self.symmetry_x]

    @udebs.countrecursion
    @connect4_cache
    def negamax(self, alpha=-1, beta=1):
        value = -float("inf")
        for child, e in self.substates():
            if child is e:
                result = child
            else:
                result = -child.negamax(-beta, -alpha)

            if result > value:
                value = result
                if result > alpha:
                    alpha = result

            if alpha >= beta:
                return value

        return value

def modifyconfig(config, x, y):
    tree = ET.parse(config)
    root = tree.getroot()

    root.find("map/dim/x").text = str(x)
    root.find("map/dim/y").text = str(y)

    return ET.tostring(root)

class Connect4(Games):
    def createTemplate(self):
        data_path = pathlib.Path(__file__).parent / "data" / f"data-{self.x}x{self.y}.pkl"
        with (data_path).open("rb") as f:
            self.data_storage = pickle.load(f)

        config = modifyconfig(udebs_config.config, self.x, self.y)
        main_map = udebs.battleStart(config, field=Connect4_core())
        main_map.data_storage = self.data_storage
        main_map.state[0].data_storage = self.data_storage
        return main_map

class Connect4_4x4(Connect4):
    x = 4
    y = 4

class Connect4_5x4(Connect4):
    x = 5
    y = 4

class Connect4_5x5(Connect4):
    x = 5
    y = 5

# class Connect4_6x5(Connect4):
#     x = 5
#     y = 5