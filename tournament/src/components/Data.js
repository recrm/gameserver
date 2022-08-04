import React from "react";
import ls from "local-storage";
import { restorePlayer, by_player } from "./Player";


export const DataOutput = (props) => {
    let data = JSON.stringify(compress(props.state), undefined, 4);
    return (
        <div>
            <h1>Export Data</h1>
            <textarea value={data} readOnly />
        </div>
    );
}

export class DataManager extends React.Component {
    state = {
        raw: "",
        error: "",
    }

    getNew() {
        this.props.newState(new_local());
        this.props.newState({page: "players"});
    }

    getFromLocal() {
        let data = ls.get("ak-rc_games");
        if (data !== null) {
            let new_state = JSON.parse(data);
            expand(new_state, this.props.newState);
            this.props.newState(new_state);
            this.props.newState({page: "players"});
        }
    }

    getFromText() {
        try {
            let new_state = JSON.parse(this.state.raw);
            expand(new_state, this.props.newState);
            this.props.newState(new_state);
            this.props.newState({page: "players"});
        } catch(SyntaxError) {
            this.setState({error: "Failed to load data"});
        }
    }

    onChangeData(event) {
        this.setState({raw: event.target.value});
    }

    render() {
        return (
            <div>
                <h1>Load Data</h1>
                <div className="buttons">
                    <button onClick={this.getNew.bind(this)}>New Event</button>
                    <button onClick={this.getFromLocal.bind(this)}>Previous Event</button>
                    <button onClick={this.getFromText.bind(this)}>Import</button>
                </div>
                <div>
                    <textarea onChange={this.onChangeData.bind(this)} />
                    <p className="error">{this.state.error}</p>
                </div>
            </div>
        )
    }
}

function expand(obj, newState) {
    obj.players.forEach(x => restorePlayer(x, () => newState({players: obj.players})));

    obj.rounds.forEach(round => {
        round.forEach((match, index, theArray) => {
            theArray[index] = [
                {
                    player: match.key1 === -1
                        ? by_player
                        : obj.players[match.key1],
                    score: match.score1,
                },
                {
                    player: match.key2 === -1
                        ? by_player
                        : obj.players[match.key2],
                    score: match.score2,
                }
            ];
        })
    });
    return obj
}

function compress(obj) {
    let copy = JSON.parse(JSON.stringify(obj));
    copy.rounds.forEach(round => {
        round.forEach((match, index, theArray) => {
            theArray[index] = {
                key1: match[0].player.key,
                key2: match[1].player.key,
                score1: match[0].score,
                score2: match[1].score,
            }
        })
    });
    delete copy.page;
    return copy;
}

export function save_local(obj) {
    let data = compress(obj);
    ls.set("ak-rc_games", JSON.stringify(data));
}

export function load_local(newState) {
    let data = ls.get("ak-rc_games");
    if (data !== null) {
        let new_state = JSON.parse(data);
        return expand(new_state, newState);
    }
}

export function new_local() {
    return {
        players: [],
        rounds: [],
        topcut: [],
        topcut_rounds: [],
    };
}