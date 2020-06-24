import uuid
from flask import request, Blueprint, current_app
from functools import wraps


def new_blueprint(name, games):
    app = Blueprint(name, __name__)
    storage = games()

    def safeGet(game, value):
        raw = request.form.get(value, "empty")
        if "," in raw:
            split = raw.split(",")
            split[0] = int(split[0])
            split[1] = int(split[1])
            raw = tuple(split)

        return raw

    def check_id(f):
        @wraps(f)
        def wrapper(gameid, *args, **kwargs):
            if gameid not in storage.games:
                current_app.logger.info(f"Game id not found: {gameid}")
                return {"message": "Game id not found"}, 404

            return f(gameid, *args, **kwargs)

        return wrapper

    @app.route("/new/<solver>", methods=["GET"])
    def create_connect4(solver):
        gameid = str(uuid.uuid4())
        game = storage.createNew()
        storage.games[gameid] = game
        current_app.logger.info(f"game created: {gameid}")

        return {
            "gameid": gameid,
            "state": game.to_json(solver == "children")
        }

    @app.route("/<gameid>/<solver>", methods=["GET"])
    @check_id
    def view_connect4(gameid, solver):
        game = storage.games[gameid]
        current_app.logger.info(f"game viewed: {gameid}")
        return {
            "gameid": gameid,
            "state": game.to_json(solver == "children"),
        }

    @app.route("/<gameid>/update/<solver>", methods=["POST"])
    @check_id
    def update_connect4(gameid, solver):
        game = storage.games[gameid]

        caster = safeGet(game, "caster")
        target = safeGet(game, "target")
        move = safeGet(game, "move")

        update = game.castMove(caster, target, move)
        if update:
            game.controlTime()
            current_app.logger.info(f"game updated: {gameid}")
        else:
            current_app.logger.info(f"game not updated: {gameid}")
            current_app.logger.info(f"{caster} {target} {move}")

        v = {
            "gameid": gameid,
            "accepted": update,
            "state": game.to_json(solver == "children"),
        }
        return v

    @app.route("/<gameid>/revert/<solver>", methods=["GET"])
    @check_id
    def revert_connect4(gameid, solver):
        game = storage.games[gameid]
        new_game = game.getRevert(1)
        if new_game:
            storage.games[gameid] = new_game
            game = new_game
            current_app.logger.info(f"game reverted: {gameid}")
        else:
            current_app.logger.info(f"game not reverted: {gameid}")

        return {
            "gameid": gameid,
            "accepted": True if new_game else False,
            "state": game.to_json(solver == "children"),
        }

    @app.route("/<gameid>/reset/<solver>", methods=["GET"])
    @check_id
    def reset_connect4(gameid, solver):
        storage.games[gameid].resetState()
        current_app.logger.info(f"game reset: {gameid}")
        return {
            "gameid": gameid,
            "accepted": True,
            "state": storage.games[gameid].to_json(solver == "children"),
        }

    return app
