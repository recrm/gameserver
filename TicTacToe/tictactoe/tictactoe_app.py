from browser import document, bind
from tictactoe import game
from tictactoe.opening_book import main_storage
import random


def update(state, field, storage):
    # Update Next
    token = ""
    if field.value is None:
        token = "x" if field.time % 2 == 0 else "o"

    if token != state["next"]:
        selection = f".game-controls .game-circle"
        node = document.select(selection)[0]
        node.attrs["class"] = f"game-circle {token}"
        state["next"] = token

    # Update played
    map_ = field.map["map"]
    for x, y, __ in map_:
        token = map_[(x, y)]
        data = state["squares"][(x, y)]

        # Check token
        if token != data["token"]:
            selection = f".game-board .game-row:nth-child({x + 1}) .game-square:nth-child({y + 1}) .game-circle"
            node = document.select(selection)[0]
            node.attrs["class"] = f"game-circle {token}"
            data["token"] = token

        # Check hint
        value = None
        if state["hint"] and state["next"] and data["token"] == "empty":
            new = field.castFuture(f"{state['next']}Player", (x, y), "placement")
            value = new.solve(storage)

        if value != data["hint"]:
            if value == -1:
                result = "win"
            elif value == 1:
                result = "lose"
            elif value == 0:
                result = "tie"
            else:
                result = ""

            selection = f".game-board .game-row:nth-child({x + 1}) .game-square:nth-child({y + 1})"
            node = document.select(selection)[0]
            node.attrs["class"] = f"game-square {result}"
            data["hint"] = value


def init(state, field, storage):
    for x in range(3):
        for y in range(3):
            state["squares"][(x, y)] = {
                "token": "empty",
                "hint": None,
            }

    state["hint"] = document["hide"].checked
    update(state, field, storage)


main_map = game.start_game()
main_state = {
    "next": "x",
    "hint": False,
    "squares": {},
}

init(main_state, main_map, main_storage)


@bind(document["reset"], "click")
def click_reset(event):
    main_map.resetState()
    update(main_state, main_map, main_storage)


@bind(document.select(".game-row > .game-square"), "click")
def move_next(event):
    x, y = event.currentTarget.attrs["data-internalid"]
    if main_state["next"]:
        token = f"{main_state['next']}Player"
        main_map.castMove(token, (int(x), int(y)), "placement")
        update(main_state, main_map, main_storage)


@bind(document["undo"], "click")
def click_undo(event):
    global main_map
    new = main_map.getRevert(1)
    if new:
        main_map = new
        update(main_state, main_map, main_storage)


@bind(document["hide"], "change")
def switch_hide(event):
    main_state["hint"] = event.currentTarget.checked
    update(main_state, main_map, main_storage)


@bind(document["ai"], "click")
def click_ai(event):
    data = {}

    for move in main_map.legalMoves():
        new = main_map.castFuture(*move)
        value = new.solve(main_storage)
        if value not in data:
            data[value] = []

        data[value].append(move)

    if len(data) == 0:
        return

    if -1 in data:
        played_move = random.choice(data[-1])
    elif 0 in data:
        played_move = random.choice(data[0])
    else:
        played_move = random.choice(data[1])

    main_map.castMove(*played_move)
    update(main_state, main_map, main_storage)
