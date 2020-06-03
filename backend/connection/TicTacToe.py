from .core import Connection, ConnectionManager
from . import udebs_config

class TicTacToe(Connection):
    def fullChildren(self):
        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        map_ = self.map["map"]
        for loc, value in map_.items():
            if value == "empty":
                yield player, loc, "placement"

    def legalMoves(self):
        map_ = self.map["map"]

        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        other = self.getStat("oPlayer" if player == "xPlayer" else "xPlayer", "token")
        token = self.getStat(player, "token")

        options = []
        forced = None

        for loc in map_:
            if map_[loc] == "empty":
                position = player, loc, "placement"

                self_pairs = udebs_config.win(map_, token, loc)

                # First check if we win here.
                if self_pairs >= self.win_cond:
                    yield -1
                    return

                # we are in check, must play here
                elif udebs_config.win(map_, other, loc) >= self.win_cond:
                    if forced is None:
                        forced = position
                    else:
                        forced = 1

                elif forced is None:
                    options.append((
                        *position,
                        self_pairs
                    ))

        if forced is not None:
            yield forced
        elif len(options) == 0:
            yield 0
        else:
            yield from sorted(options, key=lambda x: x[3], reverse=True)

    #---------------------------------------------------
    #                 Main Symmetries                  -
    #---------------------------------------------------
    def hash(self):
        """Return an immutable representation of a game map."""
        mappings = {
            "empty": "0",
            "x": "1",
            "o": "2"
        }

        map_ = self.map["map"]
        rows = []
        for y in range(map_.y):
            buf = ''
            for x in range(map_.x):
                buf += mappings[map_[(x,y)]]
            rows.append(buf)

        sym_y = lambda x: list(reversed(x))
        sym_90 = lambda x: ["".join(reversed(x)) for x in zip(*x)]

        syms = [rows]
        for i in range(3):
            syms.append(sym_90(syms[-1]))

        syms.append(sym_y(syms[0]))
        for i in range(3):
            syms.append(sym_90(syms[-1]))

        return min(int("".join(i), 3) for i in syms)

#---------------------------------------------------
#                 Managers                         -
#---------------------------------------------------
class Tictactoe_3x3(ConnectionManager):
    x = 3
    y = 3
    maxsize = 2**10
    type = "tictactoe"
    field=TicTacToe
    win_cond = 3

class Tictactoe_4x4(ConnectionManager):
    x = 4
    y = 4
    maxsize = 2**18 # ~ 32 MB
    type = "tictactoe"
    field=TicTacToe
    win_cond = 4

class Tictactoe_5x5(ConnectionManager):
    x = 5
    y = 5
    maxsize = float("inf") # ~ 128 MB
    type = "tictactoe"
    field=TicTacToe
    win_cond = 4