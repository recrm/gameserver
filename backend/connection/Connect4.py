from . import core, udebs_config

class Connect4_core(core.Connection):
    def legalMoves(self):
        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        for x in range(self.map["map"].x):
            yield player, (x, 0), "drop"

    def legalMoves2(self, map_):
        token = "x" if map_.playerx else "o"
        other = ("o" if token == "x" else "x")

        options = []
        forced = None
        backup = None

        stones = len(map_) - map_.time

        # First yield score of surrender
        yield int(stones / 2)

        for x in range(map_.x):
            y = udebs_config.BOTTOM(map_, x)
            if y is not None:
                loc = (x, y)
                position = token, loc, "drop"

                # First check if we win here.
                win_me = udebs_config.win(map_, token, loc)
                if win_me >= self.win_cond:
                    yield -int((stones + 1) / 2)
                    return

                if forced is None:
                    win_you = udebs_config.win(map_, other, loc)
                    if win_you >= self.win_cond:
                        # we are in check, must play here
                        forced = position
                        continue

                    if y > 0:
                        above_you = udebs_config.win(map_, other, (x, y - 1))
                        if above_you >= self.win_cond:
                            # We cannot play here unless it is our only option
                            backup = int((stones + 2) / 2)
                            continue

                    # finally these are our only good options
                    options.append((
                        *position,
                        win_me,
                    ))

        if forced:
            yield forced
            return
        elif len(options) == 0:
            yield backup if backup else 0
            return

        huristic = lambda x: (x[3], -abs(((map_.x - 1) / 2) - x[1][0]))
        yield from sorted(options, key=huristic, reverse=True)

    #---------------------------------------------------
    #                 Main Symmetries                  -
    #---------------------------------------------------
    def hash(self, map_):
        mappings = {
            "empty": "0",
            "x": "1",
            "o": "2",
        }

        data = []
        sym = []
        for y in range(map_.y):
            buf = [mappings[map_[x,y]] for x in range(map_.x)]
            data.extend(buf)
            sym.extend(reversed(buf))

        return min(int("".join(data), 3), int("".join(sym), 3))

#---------------------------------------------------
#                 Managers                         -
#---------------------------------------------------
class Connect4_4x4(core.ConnectionManager):
    x = 4
    y = 4
    maxsize = 2**14 # ~ 2 MB
    type = "Connect4"
    field=Connect4_core
    win_cond = 4

class Connect4_5x4(core.ConnectionManager):
    x = 5
    y = 4
    maxsize = 2**18 # ~ 32 MB
    type = "Connect4"
    field=Connect4_core
    win_cond = 4

class Connect4_5x5(core.ConnectionManager):
    x = 5
    y = 5
    maxsize = 2**22 # ~ 512MB
    type = "Connect4"
    field=Connect4_core
    win_cond = 4

class Connect4_6x5(core.ConnectionManager):
    x = 6
    y = 5
    maxsize = 2**22 # ~ 512MB
    type = "Connect4"
    field=Connect4_core
    win_cond = 4