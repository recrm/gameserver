import udebs
from . import game, udebs_config
import pickle
from collections import OrderedDict

def process(alpha, beta, main_map, storage):

    main_map = udebs.modifystate(main_map, {
        "drop": {"group": []},
        "xPlayer": {"immutable": True},
        "oPlayer": {"immutable": True},
    })

    value = main_map.negamax(alpha, beta, storage=storage)
    print("finished", alpha, beta, "as", value)
    return value

def iterate(main_map, depth, storage):
    process(-1, 1, main_map, storage)
    if depth > 0:
        [iterate(i, depth-1, storage) for i, e in main_map.substates(main_map.fullChildren())]

def generate():
    for x,y in [(4,4), (5,4), (5,5)]:
        new = game.modifyconfig(udebs_config.config, x, y)

        main_map = udebs.battleStart(new, field=game.Connect4_core())

        depth = 3
        storage = OrderedDict()
        iterate(main_map, depth, storage)

        path = f"/home/ryan/local/gamesserver/backend/connect4/data/data-{x}x{y}.pkl"

        with open(path, "wb+") as f:
            pickle.dump(storage, f)

        print("saved to", path)

        print("book size", len(storage))
