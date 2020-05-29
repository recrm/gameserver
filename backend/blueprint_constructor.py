import uuid
from flask import request, Blueprint, current_app
from functools import wraps

def new_blueprint(name, Games):
    app = Blueprint(name, __name__)
    storage = Games()

    def safeGet(game, value):
        raw = request.form.get(value, "empty")
        if "," in raw:
            split = raw.split(",")
            split[0] = int(split[0])
            split[1] = int(split[1])
            raw = tuple(split)

        return raw

    def checkid(f):
        @wraps(f)
        def wrapper(gameid):
            if gameid not in storage.games:
                current_app.logger.info(f"Game id not found: {gameid}")
                return {"message": "Game id not found"}, 404

            return f(gameid)

        return wrapper

    @app.route("/new", methods=["GET"])
    def create_connect4():
        gameid = str(uuid.uuid4())
        game = storage.createNew()
        storage.games[gameid] = game
        current_app.logger.info(f"game created: {gameid}")

        return {
            "gameid": gameid,
            "state": game.to_json()
        }

    @app.route("/<gameid>", methods=["GET"])
    @checkid
    def view_connect4(gameid):
        game = storage.games[gameid]
        current_app.logger.info(f"game viewed: {gameid}")
        return {
            "gameid": gameid,
            "state": game.to_json(),
        }

    @app.route("/<gameid>/update", methods=["POST"])
    @checkid
    def update_connect4(gameid):
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
            "state": game.to_json(),
        }
        return v

    @app.route("/<gameid>/revert", methods=["GET"])
    @checkid
    def revert_connect4(gameid):
        game = storage.games[gameid]
        new_game = game.getRevert(1)
        if new_game:
            storage.games[gameid] = new_game
            current_app.logger.info(f"game reverted: {gameid}")
        else:
            current_app.logger.info(f"game not reverted: {gameid}")

        return {
            "gameid": gameid,
            "accepted": True if new_game else False,
            "state": new_game.to_json() if new_game else game.to_json(),
        }

    @app.route("/<gameid>/reset", methods=["GET"])
    @checkid
    def reset_connect4(gameid):
        storage.games[gameid].resetState()
        current_app.logger.info(f"game reset: {gameid}")
        return {
            "gameid": gameid,
            "accepted": True,
            "state": storage.games[gameid].to_json(),
        }

    @app.route("/<gameid>/delete", methods=["GET"])
    @checkid
    def delete_connect4(gameid):
        del storage.games[gameid]
        current_app.logger.info(f"game deleted: {gameid}")
        return {
            "gameid": gameid,
            "accepted": True
        }

    return app