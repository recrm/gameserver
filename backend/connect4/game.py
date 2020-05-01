import udebs
import pathlib
import json

from ..core import Core, Games

@udebs.register({"args": ["$1", "$2"]})
def BOTTOM(map_, x):
    for y in range(map_.y -1, -1, -1):
        if map_[(x, y)] == "empty":
            return y

@udebs.register({"args": ["$1", "$2", "$3"]})
def ENDSTATE(map_, token, loc):
    maxim = 0

    for x_, y_ in ((1,0), (0,1), (1,1)):
        count = -1
        for d_ in (1, -1):
            x_ *= d_
            y_ *= d_

            new, centre = token, loc
            while new == token:
                count +=1
                centre = centre[0] + x_, centre[1] + y_
                try:
                    new = map_[centre]
                except IndexError:
                    break

        if count > maxim:
            maxim = count

    if maxim >= 4:
        return 1 if token == "x" else -1

    if "empty" in map_.values():
        return None

    return 0

path_data = pathlib.Path(__file__).parent / "data.json"
path_config = pathlib.Path(__file__).parent / "config.xml"

class Connect4_core(Core):
    results_data = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if Connect4_core.results_data is None:
            with open(path_data) as f:
                Connect4_core.results_data = json.load(f)

    @property
    def symmetries(self):
        return [self.symmetry_x]

class Connect4(Games):
    def createTemplate(self):
        return udebs.battleStart(path_config, field=Connect4_core())