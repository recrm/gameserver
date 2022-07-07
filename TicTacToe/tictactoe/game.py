from udebs import register, Instance
import functools


# Setup Udebs
@register(["self"])
def ENDSTATE(state):
    def rows(game_map):
        """Iterate over possible win conditions in game map."""
        size = len(game_map)

        for i_ in range(size):
            yield game_map[i_]
            yield [j[i_] for j in game_map]

        yield [game_map[i_][i_] for i_ in range(size)]
        yield [game_map[size - 1 - i_][i_] for i_ in range(size)]

    # Check for a win
    tie = True
    for i in rows(state.map["map"].map):
        value = set(i)
        if "empty" in value:
            tie = False
        elif len(value) == 1:
            if i[0] == "x":
                return 1
            elif i[0] == "o":
                return -1

    if tie:
        return 0


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


def alpha_beta_cache(f, maxsize=2 ** 20):
    empty = (-float("inf"), float("inf"))

    @functools.wraps(f)
    def cache_wrapper(self, alpha, beta, map_, storage):
        key = self.hash(map_)

        a_, b_ = storage.get(key, empty)
        if a_ > alpha:
            alpha = a_

        if b_ < beta:
            beta = b_

        if alpha >= beta:
            # Note: Alpha and beta may not be the same.
            # Returning either will produce the right answer, but
            # it is unclear which is more efficient.
            return alpha

        result = f(self, alpha, beta, map_, storage)
        if result <= alpha:
            storage[key] = (a_, result)
        elif result >= beta:
            storage[key] = (result, b_)
        else:
            storage[key] = (result, result)

        return result

    return cache_wrapper


class TicTacToe(Instance):
    def legalMoves(self):
        if self.value:
            return

        player = "xPlayer" if self.time % 2 == 0 else "oPlayer"
        map_ = self.map["map"]
        yield from ((player, loc, "placement") for loc in map_ if map_[loc] == "empty")

    @staticmethod
    def scanMoves(map_):
        token, other = ("x", "o") if map_.playerx else ("o", "x")
        options = []
        forced = None

        for loc in map_:
            if map_[loc] == "empty":

                # First check if we win here.
                if win(map_, token, loc) >= 3:
                    yield -1
                    return

                # we are in check, must play here
                if win(map_, other, loc) >= 3:
                    if forced:
                        yield 1
                        return
                    forced = token, loc
                elif forced is None:
                    options.append((token, loc))

        if forced:
            yield forced
            return
        elif len(options) == 0:
            yield 0
            return
        else:
            yield from options

    @staticmethod
    def hash(map_):
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

        symmetries = [rows]
        for i in range(3):
            symmetries.append(sym_90(symmetries[-1]))

        symmetries.append(sym_y(symmetries[0]))
        for i in range(3):
            symmetries.append(sym_90(symmetries[-1]))

        return min(int("".join(i), 3) for i in symmetries)

    @alpha_beta_cache
    def result(self, alpha, beta, map_, storage):
        current = -float("inf")
        for move in self.scanMoves(map_):
            try:
                token, loc = move
            except TypeError:
                computed = -move
            else:
                new = map_.copy()
                new.playerx = not map_.playerx
                new[loc] = token
                computed = -self.result(-beta, -alpha, new, storage)

            if computed > current:
                current = computed
                if computed > alpha:
                    alpha = computed
                    if alpha >= beta:
                        break

        return current

    def solve(self, storage):
        if self.value is not None:
            return -abs(self.value)

        # prepare map for processing
        new = self.map["map"].copy()
        new.playerx = self.time % 2 == 0
        return self.result(-1, 1, new, storage)


def start_game():
    return TicTacToe(
        logging=False,
        name="tictactoe",
        immutable=True,
        stats={"ACT"},
        strings={"token"},
        map=[{
            "name": "map",
            "dim": (3, 3),
        }],
        revert=10,
        entities=[
            {"name": "player"},
            {
                "name": "tick",
                "require": [
                    "score = (ENDSTATE)",
                    "$score != None",
                ],
                "effect": "EXIT $score",
            },
            {
                "immutable": False,
                "name": "xPlayer",
                "group": "player",
                "ACT": 2,
                "token": "x",
            },
            {
                "immutable": False,
                "name": "oPlayer",
                "group": "player",
                "ACT": 1,
                "token": "o",
            },
            {"name": "x"},
            {"name": "o"},
            {
                "name": "placement",
                "require": [
                    "$caster.STAT.ACT &gt;= 2",
                    "$target.NAME == empty",
                    "VAR.value == None",
                ],
                "effect": [
                    "#($caster.STAT.token) RECRUIT $target",
                    "$caster ACT -= 2",
                    "ALL.player ACT += 1",
                ]
            },
            {
                "name": "reset",
                "effect": [
                    "#empty MOVE (FILL (0 0))",
                    "#xPlayer ACT REPLACE 2",
                    "#oPlayer ACT REPLACE 1",
                ]
            }
        ]
    )
