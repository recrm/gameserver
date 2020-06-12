from . import managers
import pickle
from collections import OrderedDict
import udebs

def iterate(main_map, depth):
    if depth > 0:
        for child, e in main_map.substates():
            iterate(child, depth-1)

    key = main_map.hash(main_map.getMap())
    if key not in main_map.start_book:
        print(key)
        main_map.start_book[key] = main_map.result(-1, 1)

def generate():
    for manager in managers:

        data_manager = manager()
        main_map = data_manager.createNew()

        depth = 3
        with udebs.Timer():
            iterate(main_map, depth)

        with open(data_manager.path, "wb+") as f:
            pickle.dump(main_map.storage, f)

        with open(data_manager.book_path, "wb+") as f:
            pickle.dump(main_map.start_book, f)

        print("saved to", data_manager.path)
        print("storage size", len(main_map.storage))
        print("book size", len(main_map.start_book))

        print()
