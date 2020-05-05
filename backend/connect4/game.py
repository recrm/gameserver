import udebs
import pathlib
import json
import random

from ..core import Core, Games

@udebs.register({"args": ["$1", "$2"]})
def BOTTOM(map_, x):
    for y in range(map_.y -1, -1, -1):
        if map_[(x, y)] == "empty":
            return y

@udebs.register({"args": ["$1", "$2", "$3"]})
def ENDSTATE(map_, token, loc):
    maxim = 0

    for x_, y_ in ((1,0), (0,1), (1,1), (1, -1)):
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

with open(path_data) as f:
    data = json.load(f)

@udebs.register({"args": ["self", "$1"]})
def COMPUTER(state, player):
    current = state.pState()
    canon = min(f(current) for f in state.symmetries)
    score = 1 if player == "xPlayer" else -1

    # Get all possible replies.
    replies = []
    for _i in (1, 0, -1):
        for child in data[canon]["children"]:
            if data[child]["result"] == (score * _i):
                replies.append(child)

        # We only want the best, break if we have found any.
        if len(replies) > 0:
            break

    # Now filter symettries to only those that we need.
    final = []
    for reply in replies:
        for f in state.symmetries:
            new = f(reply)
            if state.stringDistance(current, new) == 1:
                final.append(new)

    # Cool now pick one
    choice = random.choice(final)

    # Now we figure out what column was dropped in.
    i = 0
    for x,y in zip(current, choice):
        if x != y:
            break
        i +=1

    cols = state.map["map"].x + 1
    col = (i % cols)
    return (col, 0, "map")

class Connect4_core(Core):
    results_data = data

    @property
    def symmetries(self):
        return [self.identity, self.symmetry_x]

class Connect4(Games):
    def createTemplate(self):
        return udebs.battleStart(path_config, field=Connect4_core())