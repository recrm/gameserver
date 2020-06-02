from . import core, udebs_config

class Connect4_core(core.Connection):
    def fullChildren(self):
        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        for x in range(self.map["map"].x):
            yield player, (x, 0), "drop"

    def legalMoves(self):
        map_ = self.map["map"]
        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        other = self.getStat("oPlayer" if player == "xPlayer" else "xPlayer", "token")
        token = self.getStat(player, "token")

        options = []
        forced = None
        backup = None

        for x in range(map_.x):
            y = udebs_config.BOTTOM(map_, x)
            if y is not None:
                loc = (x,y)
                position = player, loc, "drop"
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
                    # This would put us in check, can't play here
                    if y > 0 and udebs_config.win(map_, other, (x, y - 1)) >= self.win_cond:
                        backup = 1
                    else:
                        options.append((
                            *position,
                            self_pairs,
                            -abs(((map_.x - 1) / 2) - x)
                        ))

        if forced:
            yield forced
        elif len(options) == 0:
            yield backup if backup else 0
        else:
            yield from sorted(options, key=lambda x: x[3:5], reverse=True)

    #---------------------------------------------------
    #                 Main Symmetries                  -
    #---------------------------------------------------
    @staticmethod
    def symmetry_x(split):
        split = split.split("|")
        return "|".join(i[::-1] for i in split)

    @property
    def symmetries(self):
        return [self.identity, self.symmetry_x]

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