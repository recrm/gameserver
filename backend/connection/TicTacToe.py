from .core import Connection, ConnectionManager
from . import udebs_config


class TicTacToe(Connection):
    def legalMoves(self):
        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        map_ = self.map["map"]
        for loc, value in map_.items():
            if value == "empty":
                yield player, loc, "placement"

    def legalMoves2(self, map_):
        token = "x" if map_.playerx else "o"
        other = ("o" if token == "x" else "x")

        options = []
        forced = None

        for loc in map_:
            if map_[loc] == "empty":
                position = token, loc, "placement"

                # First check if we win here.
                win_me = udebs_config.win(map_, token, loc)
                if win_me >= self.win_cond:
                    yield -1
                    return

                # we are in check, must play here
                if forced is None:
                    win_you = udebs_config.win(map_, other, loc)
                    if win_you >= self.win_cond:
                        forced = position
                        continue

                    options.append((
                        *position,
                        win_me
                    ))

        if forced:
            yield forced
            return
        elif len(options) == 0:
            yield 0
            return
        else:
            yield from sorted(options, key=lambda x: x[3], reverse=True)

    # ---------------------------------------------------
    #                 Main Symmetries                  -
    # ---------------------------------------------------
    def hash(self, map_):
        """Return an immutable representation of a game map."""
        mappings = {
            "empty": "0",
            "x": "1",
            "o": "2"
        }

        rows = []
        for y in range(map_.y):
            buf = [mappings[map_[x, y]] for x in range(map_.x)]
            rows.append("".join(buf))

        def sym_y(row):
            return list(reversed(row))

        def sym_90(row):
            return ["".join(reversed(x_)) for x_ in zip(*row)]

        syms = [rows]
        for i in range(3):
            syms.append(sym_90(syms[-1]))

        syms.append(sym_y(syms[0]))
        for i in range(3):
            syms.append(sym_90(syms[-1]))

        return min(int("".join(i), 3) for i in syms)


# ---------------------------------------------------
#                 Managers                         -
# ---------------------------------------------------
class Tictactoe_3x3(ConnectionManager):
    x = 3
    y = 3
    maxsize = 2 ** 4
    type = "tictactoe"
    field = TicTacToe
    win_cond = 3


class Tictactoe_4x4(ConnectionManager):
    x = 4
    y = 4
    maxsize = 2 ** 15  # ~ 32 MB
    type = "tictactoe"
    field = TicTacToe
    win_cond = 4


class Tictactoe_5x5(ConnectionManager):
    x = 5
    y = 5
    maxsize = float("inf")  # ~ 128 MB
    type = "tictactoe"
    field = TicTacToe
    win_cond = 4
