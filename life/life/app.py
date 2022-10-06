from browser import document, bind, html, timer
import logging
from life import game
logging.basicConfig(level=logging.INFO)


def update(state, field):
    # update speed
    current_speed = document.select("#speed")[0].value
    if current_speed != state["speed"]:
        document.select("#speed")[0].value = state["speed"]

    # update pause
    current_pause = document.select("#pause")[0].text
    intended = "Unpause" if main_state["pause"] else "Pause"
    if current_pause != intended:
        document.select("#pause")[0].text = intended

    # update seed
    current_seed = int(document.select("#seed")[0].value)
    if current_seed != state["seed"]:
        document.select("#seed")[0].value = state["seed"]

    map_ = field.getMap()
    for x, y, _ in field.getMap():
        unit = map_[(x, y)]

        selection = f".game-board .game-row:nth-child({x + 1}) .game-square:nth-child({y + 1})"
        node = document.select(selection)[0]
        if field[unit].LIFE:
            intended = f"game-square alive"
        else:
            intended = f"game-square dead"

        if node.attrs["class"] != intended:
            node.attrs["class"] = intended


main_state = {
    "pause": True,
    "speed": 10,
    "seed": 600,
    "timer_id": 1,
}

main_map = game.start_game()

main_div = document.select(".game-grid")[0]
for x in range(main_map.getMap().x):
    row = html.DIV(Class="game-row")
    for y in range(main_map.getMap().y):
        square = html.DIV(Class="game-square dead")
        square.attrs["data-internalid"] = f"{x}{y}"
        row <= square

    main_div <= row

update(main_state, main_map)


def forward():
    main_map.controlTime(1)
    update(main_state, main_map)
    speed = 100 / main_state["speed"]
    main_state["timer_id"] = timer.set_timeout(forward, speed)


@bind(document.select(".game-row > .game-square"), "click")
def manual_change(event):
    x, y = event.currentTarget.attrs["data-internalid"]
    entity = main_map.getEntity((int(x), int(y), "map"))
    main_map.castMove(entity, entity, main_map["manual_change"], time=0)
    update(main_state, main_map)


@bind(document["reset"], "click")
def click_reset(event):
    main_map.rand.seed(main_state["seed"])
    main_map.resetState()
    update(main_state, main_map)


@bind(document["pause"], "click")
def click_pause(event):
    main_state["pause"] = not main_state["pause"]

    if not main_state["pause"]:
        speed = 100 / main_state["speed"]
        main_state["timer_id"] = timer.set_timeout(forward, speed)
    else:
        timer.clear_timeout(main_state["timer_id"])

    update(main_state, main_map)


@bind(document["speed"], "change")
def click_speed(event):
    main_state["speed"] = int(event.target.value)
    print(main_state["speed"])
    update(main_state, main_map)


@bind(document["seed"], "change")
def click_seed(event):
    main_state["seed"] = int(event.target.value)
    update(main_state, main_map)


@bind(document["right"], "click")
def click_right(event):
    if main_state["pause"]:
        main_map.controlTime(1)
        update(main_state, main_map)


@bind(document["left"], "click")
def click_left(event):
    if main_state["pause"]:
        global main_map
        new_map = main_map.getRevert(1)
        if new_map is not None:
            main_map = new_map
            update(main_state, main_map)
