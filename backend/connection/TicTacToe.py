from .core import Connection, ConnectionManager
from . import udebs_config

class TicTacToe(Connection):
    def fullChildren(self):
        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        map_ = self.map["map"]
        for loc in map_:
            if map_[loc] == "empty":
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

                # First check if we win here.
                if udebs_config.win(map_, token, loc) >= self.win_cond:
                    yield 1
                    return

                # we are in check, must play here
                elif udebs_config.win(map_, other, loc) >= self.win_cond:
                    if forced is None:
                        forced = position
                    else:
                        forced = -1

                elif forced is None:
                    options.append((
                        *position,
                        udebs_config.win(map_, token, loc)
                    ))

        if forced is not None:
            yield forced
        elif len(options) == 0:
            yield 0
        else:
            yield from sorted(options, key=lambda x: x[3], reverse=True)

    @property
    def symmetries(self):
        return [self.identity, self.symmetry_x, self.symmetry_y, self.symmetry_90, self.symmetry_180, self.symmetry_270]

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
    maxsize = 2**19 # ~ 64 MB
    type = "tictactoe"
    field=TicTacToe
    win_cond = 4

class Tictactoe_5x5(ConnectionManager):
    x = 5
    y = 5
    maxsize = 2**20 # ~ 128 MB
    type = "tictactoe"
    field=TicTacToe
    win_cond = 4