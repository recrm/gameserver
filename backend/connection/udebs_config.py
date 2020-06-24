import pathlib
from collections import OrderedDict

import udebs

config = pathlib.Path(__file__).parent / "config.xml"


@udebs.register(["$1", "$2"])
def BOTTOM(map_, x):
    for y in range(map_.y - 1, -1, -1):
        if map_[(x, y)] == "empty":
            return y


def win(map_, token, loc):
    maxim = 1
    x, y = loc[0], loc[1]
    for x_, y_ in ((1, 0), (0, 1), (1, 1), (1, -1)):
        count = 1
        for _ in (None, None):
            try:
                cx, cy = x + x_, y + y_
                while token is map_[cx, cy]:
                    count += 1
                    cx, cy = cx + x_, cy + y_
            except IndexError:
                pass

            x_ *= -1
            y_ *= -1

        if count > maxim:
            maxim = count

    return maxim


@udebs.register(["self", "$1", "$2", "$3"])
def ENDSTATE(state, map_, token, loc):
    maxim = win(map_, token, loc)

    if maxim >= state.win_cond:
        return 1 if token == "x" else -1

    if "empty" in map_.values():
        return None

    return 0


@udebs.register(["self", "$1"])
def COMPUTER(state, player):
    # Get all possible replies.
    storage = OrderedDict()
    children = [(e, -i.result(-1, 1, storage)) for i, e in state.substates()]
    replies = []
    for _i in (1, 0, -1):
        for entry, value in children:
            if value == _i:
                replies.append(entry)

        # We only want the best, break if we have found any.
        if len(replies) > 0:
            break

    # Cool now pick one
    choice = state.rand.choice(replies)

    return choice[1]
