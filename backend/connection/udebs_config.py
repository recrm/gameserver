import pathlib
import udebs

config = pathlib.Path(__file__).parent / "config.xml"

@udebs.register(["$1", "$2"])
def BOTTOM(map_, x):
    for y in range(map_.y -1, -1, -1):
        if map_[(x, y)] == "empty":
            return y

def win(map_, token, loc):
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
    children = [(e, -i.result()) for i, e in state.substates()]

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