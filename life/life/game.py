from udebs import Instance, register, Entity


@register(["$1", "$2"])
def set_gets(cell_neighbors, additions):
    new = set(cell_neighbors.neighbors)
    if isinstance(additions, Entity):
        new.add(additions.name)
    else:
        new.update(additions)

    cell_neighbors.neighbors = list(new)


def start_game():
    return Instance(
        logging=False,
        name="src",
        seed=600,
        immutable=True,
        revert=10,
        stats={"NBR", "LIFE"},
        lists={"neighbors"},
        map=[{
            "name": "map",
            "dim": (5, 5),
            "type": "diag",
        }],
        entities=[
            # Base entities
            {"name": "cell", "immutable": False},
            {
                "name": "action",
                "require": "neighbors = $target.STAT.neighbors",
                "effect": "DELAY `(set_gets #cell $neighbors) 0",
            },
            {
                "name": "manual",
                "effect": "set_gets #cell $target",
            },

            # Birth a cell.
            {
                "name": "base_life",
                "group": "action",
                "require": "$target.STAT.LIFE == 0",
                "effect": [
                    "$target LIFE REPLACE 1",
                    "DELAY `(#$neighbors NBR += 1) 0",
                ],
            },
            {
                "name": "auto_life",
                "group": "base_life",
                "require": "$target.STAT.NBR == 3",
            },
            {
                "name": "random_life",
                "group": ["base_life", "manual"],
                "require": "DICE.4 == 0",
            },

            # Kill a cell
            {
                "name": "base_death",
                "group": "action",
                "require": "$target.STAT.LIFE == 1",
                "effect": [
                    "$target LIFE REPLACE 0",
                    "DELAY `(#$neighbors NBR -= 1) 0",
                ],
            },
            {
                "name": "auto_death",
                "group": "base_death",
                "require": [
                    "nbr = $target.STAT.NBR",
                    "`($nbr < 2) OR `($nbr > 3)",
                ],
            },

            # Internal actions
            {
                "name": "init",
                "effect": [
                    "all = FILL.(1 1)",
                    "#cell RECRUIT $all",
                    "CAST #$all `($target neighbors REPLACE #(FILL $target None false 1).NAME)",
                    "CAST #$all #random_life",
                ]
            },
            {
                "name": "tick",
                "effect": [
                    "CAST #(#cell.STAT.neighbors) #auto_change",
                    "#cell CLEAR neighbors",
                ]
            },
            {
                "name": "reset",
                "effect": [
                    "all = #(FILL.(1 1))",
                    "$all NBR REPLACE 0",
                    "$all LIFE REPLACE 0",
                    "CAST #$all #random_life",
                ]
            },

            # External actions
            {
                "name": "auto_change",
                "effect": "IF $target.STAT.LIFE `(CAST.$target.#auto_death) `(CAST.$target.#auto_life)"
            },
            {
                "name": "manual_change",
                "group": "manual",
                "effect": "IF $target.STAT.LIFE `(CAST.$target.#base_death) `(CAST.$target.#base_life)"
            },
        ]
    )
