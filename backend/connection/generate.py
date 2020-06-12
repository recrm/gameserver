from . import managers
import pickle
from collections import OrderedDict
import udebs

def iterate(main_map, depth, storage, start_book):
    if depth > 0:
        for child, e in main_map.substates():
            iterate(child, depth-1, storage, start_book)

    key = main_map.hash(main_map.getMap())
    result = main_map.result(-1, 1, storage=storage)
    print(key)
    start_book[key] = result

def generate():
    for manager in managers:

        data_manager = manager()
        main_map = data_manager.createNew()

        depth = 2
        start_book = {}
        storage = OrderedDict()
        with udebs.Timer():
            iterate(main_map, depth, storage, start_book)

        with open(data_manager.path, "wb+") as f:
            pickle.dump(storage, f)

        with open(data_manager.book_path, "wb+") as f:
            pickle.dump(start_book, f)

        print("saved to", data_manager.path)

        print("storage size", len(storage))
        print("book size", len(start_book))

        print()
