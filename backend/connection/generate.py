from . import managers
import pickle
from collections import OrderedDict
import udebs

def iterate(main_map, depth, storage):
    clone = main_map.modifystate()
    clone.negamax(-1, 1, storage=storage)
    if depth > 0:
        for child, e in main_map.substates(main_map.fullChildren()):
            iterate(child, depth-1, storage)

def generate():
    for manager in managers:

        data_manager = manager()
        main_map = data_manager.createNew()

        depth = 2
        storage = OrderedDict()
        with udebs.Timer():
            iterate(main_map, depth, storage)

        with open(data_manager.path, "wb+") as f:
            pickle.dump(storage, f)

        print("saved to", data_manager.path)

        print("book size", len(storage))
        print()
