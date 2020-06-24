from . import managers
import pickle
from collections import OrderedDict
import udebs


def iterate(main_map, depth, storage):
    if depth > 0:
        for child, e in main_map.substates():
            iterate(child, depth - 1, storage)

    key = main_map.hash(main_map.getMap())
    if key not in main_map.start_book:
        main_map.start_book[key] = main_map.result(-1, 1, storage)


def generate():
    for manager in managers:
        data_manager = manager()
        main_map = data_manager.createNew()
        storage = OrderedDict()

        depth = 4
        with udebs.Timer():
            iterate(main_map, depth, storage)

        with open(data_manager.book_path, "wb+") as f:
            pickle.dump(main_map.start_book, f)

        print("saved to", data_manager.book_path)
        print("book size", len(main_map.start_book))

        print()
