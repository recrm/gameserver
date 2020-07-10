from . import core, udebs_config, data

special_data = data.results
for i in list(special_data.keys()):
    special_data[tuple(reversed(i))] = special_data[i]


class Connect4Core(core.Connection):
    def legalMoves(self):
        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        for x in range(self.map["map"].x):
            y = udebs_config.BOTTOM(self.map["map"], x)
            if y is not None:
                yield player, (x, y), "drop"

    @staticmethod
    def win_heuristic(map_, token, loc):
        token = {token, "empty"}
        maxim = 0
        x, y = loc[0], loc[1]
        for x_, y_ in ((1, 0), (0, 1), (1, 1), (1, -1)):
            sto = ["x"]
            for _ in (None, None):
                try:
                    cx, cy = x + x_, y + y_
                    while map_[cx, cy] in token:
                        sto.append("_" if map_[cx, cy] == "empty" else "x")
                        cx, cy = cx + x_, cy + y_
                except IndexError:
                    pass

                sto = list(reversed(sto))
                x_ *= -1
                y_ *= -1

            maxim += special_data.get(tuple(sto), 0)

        return maxim

    def legalMoves2(self, map_):
        yield map_.scored // 2

        token, other = ("x", "o") if map_.playerx else ("o", "x")
        options = []
        forced = False

        for x in range(map_.x):
            for y in range(map_.y - 1, -1, -1):
                if map_[x, y] == "empty":
                    break
            else:
                continue

            loc = (x, y)

            if udebs_config.win(map_, other, loc) >= self.win_cond:
                if forced:
                    return

                options = []
                forced = loc

            if not forced or forced == loc:
                if y > 0 and udebs_config.win(map_, other, (x, y - 1)) >= self.win_cond:
                    # We cannot play here unless it is our only option
                    if forced:
                        return
                else:
                    options.append(loc)

        # Lower bound optimization magic
        if len(options) > 0 and not forced:
            if map_.scored >= 2:
                yield (map_.scored - 2) // 2
        # end magic

        if len(options) > 1:
            def heuristic(row):
                return (
                    -self.win_heuristic(map_, token, row),
                    abs(map_.const - row[0])
                )

            options = sorted(options, key=heuristic)

        for loc in options:
            yield token, loc

    # ---------------------------------------------------
    #                 Main Symmetries                  -
    # ---------------------------------------------------
    @staticmethod
    def hash2(map_):
        mappings = {
            "empty": "0",
            "x": "1",
            "o": "2",
        }

        current = []
        sym = []
        for y in range(map_.y):
            buf = [mappings[map_[x, y]] for x in range(map_.x)]
            current.extend(buf)
            sym.extend(reversed(buf))

        return min(int("".join(current), 3), int("".join(sym), 3))


# ---------------------------------------------------
#                 Managers                         -
# ---------------------------------------------------
class Connect4_4x4(core.ConnectionManager):
    depth = 4
    x = 4
    y = 4
    type = "Connect4"
    field = Connect4Core
    win_cond = 4


class Connect4_5x4(core.ConnectionManager):
    depth = 4
    x = 5
    y = 4
    type = "Connect4"
    field = Connect4Core
    win_cond = 4


class Connect4_5x5(core.ConnectionManager):
    depth = 5
    x = 5
    y = 5
    type = "Connect4"
    field = Connect4Core
    win_cond = 4


class Connect4_6x5(core.ConnectionManager):
    depth = 6
    x = 6
    y = 5
    type = "Connect4"
    field = Connect4Core
    win_cond = 4
