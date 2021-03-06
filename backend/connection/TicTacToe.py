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
        other = "o" if token == "x" else "x"

        options = []
        forced = None

        for loc in map_:
            if map_[loc] == "empty":
                position = token, loc

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

                    options.append(position)

        if forced:
            yield forced
            return
        elif len(options) == 0:
            yield 0
            return
        else:
            yield from options

    # ---------------------------------------------------
    #                 Main Symmetries                  -
    # ---------------------------------------------------
    @staticmethod
    def hash2(map_):
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
    depth = 4
    x = 3
    y = 3
    type = "tictactoe"
    field = TicTacToe
    win_cond = 3


class Tictactoe_4x4(ConnectionManager):
    depth = 4
    x = 4
    y = 4
    type = "tictactoe"
    field = TicTacToe
    win_cond = 4


class Tictactoe_5x5(ConnectionManager):
    depth = 4
    x = 5
    y = 5
    type = "tictactoe"
    field = TicTacToe
    win_cond = 4
