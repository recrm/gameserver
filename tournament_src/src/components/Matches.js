import React from "react";
import { by_player } from "./Player";

export const win = 3;
export const tie = 1;
export const lose = 0;

const Match = (props) => {
    return (
        <tr key={props.name}>
            <td>{props.xname}</td>
            <td><input type="radio" value={props.xkey} name={props.name} onChange={props.onReport} checked={props.checked === props.xkey} key={1} /></td>
            <td><input type="radio" value="tie" name={props.name} onChange={props.onReport} checked={props.checked === "tie"} key={2} hidden={props.hidetie} /></td>
            <td><input type="radio" value={props.ykey} name={props.name} onChange={props.onReport} checked={props.checked === props.ykey} key={3} /></td>
            <td>{props.yname}</td>
        </tr>
    )
}

export const Round = (props) => {

    let matches = props.matches.map((x, index) => {
        let name = `${props.iden}-${index}`;

        let checked;
        if (x[0].score === win) {
            checked = x[0].player.key;
        } else if (x[1].score === win) {
            checked = x[1].player.key;
        } else if (x[0].score === tie) {
            checked = "tie";
        } else {
            checked = "noop";
        }

        return <Match
                   hidetie={props.hidetie}
                   checked={checked}
                   name={name}
                   key={index}
                   xkey={x[0].player.key}
                   ykey={x[1].player.key}
                   xname={x[0].player.name}
                   yname={x[1].player.name}
                   onReport={props.onReport}
                />
    });

    return (
        <div className="round">
            <h2>Round {props.iden + 1}</h2>
            <hr />
            <table>
                <tbody>
                    {matches}
                </tbody>
            </table>
        </div>
    );
}

export class CustomRound extends React.Component {

    state = {
        one: -1,
        two: -1,
        set: [],
        matches: [],
    }

    onChangeSelection(event) {
        if (event.target.id === "1") {
            this.setState({one: parseInt(event.target.value)});
        } else if (event.target.id === "2") {
            this.setState({two: parseInt(event.target.value)});
        }
    }

    onNextRound() {
        if (this.state.one !== this.state.two) {
            let player1 = this.state.one !== -1 ? this.props.players[this.state.one] : by_player;
            let player2 = this.state.two !== -1 ? this.props.players[this.state.two] : by_player;
            this.setState({
                matches: this.state.matches.concat([newMatch(player1, player2)]),
                set: this.state.set.concat([this.state.one, this.state.two]),
                one: -1,
                two: -1,
            });
            this.props.upperState({error: ""})
        }
    }

    onEndCustomRound() {
        this.props.newState({rounds: this.props.rounds.concat([this.state.matches])});
        this.setState({set: [], matches: []});
        this.props.upperState({custom: false, error: ""});
    }

    onAutoCustomRound() {
        let candidates = this.props.players.filter(x => !this.state.set.includes(x.key));
        let matches = pairing(candidates, this.props.rounds);

        let new_round;

        if (matches !== undefined) {
            matches.reverse();
            new_round = this.state.matches.concat(matches);
            this.props.newState({rounds: this.props.rounds.concat([new_round])});
            this.setState({set: [], matches: []});
            this.props.upperState({custom: false, error: ""});
        } else {
            this.props.upperState({error: "Could not finish round without duplicate pairings. Please finish it manually."})
        }
    }

    render() {

        let players = [by_player]
            .concat(this.props.players.filter(x => !this.state.set.includes(x.key)))
            .map(x => <option key={x.key} label={x.name}>{x.key}</option>);

        let matches = this.state.matches
            .map((x, index) => (<tr key={index}><td>{x[0].player.name}</td><td>{x[1].player.name}</td></tr>));

        return (
            <div className="round">
                <h2>Round {this.props.iden + 1}</h2>
                <hr />
                <table>
                    <tbody>
                        {matches}
                        <tr>
                            <td>
                                <select id={1} value={this.state.one} onChange={this.onChangeSelection.bind(this)}>
                                    {players}
                                </select>
                            </td>
                            <td>
                                <select id={2} value={this.state.two} onChange={this.onChangeSelection.bind(this)}>
                                    {players}
                                </select>
                            </td>
                            <td><button onClick={this.onNextRound.bind(this)}>Save</button></td>
                        </tr>
                        <tr>
                            <td><button onClick={this.onEndCustomRound.bind(this)}>Finish</button></td>
                            <td><button onClick={this.onAutoCustomRound.bind(this)}>Auto</button></td>
                        </tr>
                    </tbody>
                </table>
            </div>
        )
    }
}

export class MatchesManager extends React.Component {

    state = {
        custom: false,
        error: "",
    }

    render() {
        let matches = this.props.rounds.map(
            (x, index) => <Round
                hidetie={false}
                onReport={(event) => onRoundReport(event, this.props.rounds, this.props.newState, "rounds")}
                iden={index}
                matches={x}
                key={index}
            />
        );

        if (this.state.custom) {
            matches.push(
                <CustomRound iden={this.props.rounds.length} key={"custom"} players={this.props.players} newState={this.props.newState}
                             rounds={this.props.rounds} upperState={this.setState.bind(this)} />
            );
        }

        return (
            <div>
                <h1>Swiss Matches</h1>
                <div className="buttons">
                    <button onClick={() => onNewRound(this.props.players, this.props.rounds, this.props.newState)}>New Round</button>
                    <button onClick={() => this.setState({custom: !this.state.custom, error: ""})}>Custom Round</button>
                    <button onClick={() => onDeleteRound(this.props.rounds, this.props.newState, "rounds")}>Delete Round</button>
                </div>
                <div className="wrapper">
                    <div className="matches">
                        {matches}
                    </div>
                </div>
                <p className="error">{this.state.error}</p>
            </div>
        )
    }

}

function newMatch(player1, player2) {
    return [
        {score: player2.key === -1 ? win : lose, player: player1},
        {score: player1.key === -1 ? win : lose, player: player2},
    ]
}

function pairing(candidates, rounds) {
    if (candidates.length % 2 === 1) {
        candidates.push(by_player);
    }

    if (candidates.length === 0) {
        return [];
    }

    const node = candidates.shift();
    let opponents = node.opponents(rounds);

    return candidates
        .filter(x => !opponents.includes(x.key))
        .reduce((prev, child) => {
            if (prev !== undefined) {
                return prev;
            }

            let spliced = candidates.slice(0);
            spliced.splice(spliced.indexOf(child), 1);

            let matches = pairing(spliced, rounds);
            if (matches !== undefined) {
                matches.push(newMatch(child, node));
            }
            return matches;
        }, undefined);
}

function onNewRound(players, rounds, newState) {
    if (players.length === 0) {
        return;
    }

    let candidates = players
        .slice(0)
        .sort((a,b) => a.sort(b, players, rounds));

    let matches = pairing(candidates.slice(0), rounds);

    if (matches !== undefined) {
        matches.reverse();
        rounds.push(matches);
        newState({rounds});
    }
}

export function onDeleteRound(rounds, newState, name) {
    rounds.pop();
    newState({name: rounds});
}

export function onRoundReport(event, rounds, newState, name) {
    let round_winner = event.target.value;
    let split = event.target.name.split("-");
    let current_match = rounds[parseInt(split[0])][parseInt(split[1])];

    if (round_winner === "tie") {
        current_match.forEach((player) => {
            player.score = tie;
        });
    } else {
        current_match.forEach((player) => {
            player.score = player.player.key === parseInt(round_winner)
                ? win
                : lose;
        });
    }

    newState({[name]: rounds});
}