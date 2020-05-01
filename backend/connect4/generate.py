import json

import udebs
from udebs.treesearch import State, Result

from . import game

class Connect4(State):
    def legalMoves(self, state):
        player = "xPlayer" if state.time % 2 == 0 else "oPlayer"
        for i in range(state.map["map"].x):
            yield player, (i, 0), "drop"

    def endState(self, state):
        endstate = state.getStat("result", "result")
        return "" if endstate is None else endstate

    def pState(self, state):
        map_ = state.getMap()
        one = []
        two = []

        for y in range(map_.y):
            buf = ''
            for x in range(map_.x):
                entry = map_[x,y]
                if entry == "empty":
                    entry = "_"
                buf += entry
            one.append(buf)
            two.append(buf[::-1])

        one, two = "|".join(one), "|".join(two)
        return min(one, two)

    def result(self, state, maximizer=True, debug=False):
        pState = self.pState(state)
        if pState not in self.storage:
            value, turns = self.endState(state), 0
            children = set()

            if debug:
                print(value, turns)

            if value is None:
                results = []
                func = (max if maximizer else min)

                for substate, entry in self.substates(state):
                    if debug:
                        print(entry)
                    children.add(self.pState(substate))
                    results.append(self.result(substate, not maximizer))

                if debug:
                    print(results)
                    print(children)

                result = func(results)
                value, turns = result.value, result.turns + 1

            if debug:
                print(len(self.storage))

            self.storage[pState] = Result(value, turns)
            self.storage[pState].children = list(children)
        return self.storage[pState]

def generate():
    main_map = udebs.battleStart(game.path_config)

    storage = {}
    analyser = Connect4(storage=storage)
    with udebs.Timer():
        analysis = analyser.result(main_map, debug=True)

    database = {}
    for key, value in storage.items():
        database[key] = {
            "result": value.value,
            "turns": value.turns,
            "children": value.children,
        }

    with open(game.path_data, "w+") as f:
        json.dump(database, f)