import React from "react";
import { Round, onRoundReport, onDeleteRound, win, lose } from "./Matches"
import { by_player } from "./Player"

export class TopCut extends React.Component {
    state = {
        error: ""
    }

    newRound(people) {
        return Array
            .from(people)
            .reduce((result, value, index, array) => {
                if (index % 2 === 0) {
                    result.push(array.slice(index, index + 2));
                }
                return result;
            }, [])
            .map(x => {
                let p1 = x[0] !== -1 ? this.props.players[x[0]] : by_player;
                let p2 = x[1] !== -1 ? this.props.players[x[1]] : by_player;

                return [
                    {player: p1, score: p2.key === -1 ? win : lose},
                    {player: p2, core: p1.key === -1 ? win : lose}
                ]
            });
    }

    firstRoundPairings(topcut) {
        // Pad player count to an exponent of 16

        let cuts = topcut.slice();

        let i = 1;
        while (Math.pow(2, i) < cuts.length) {
            i += 1;
        }

        while (cuts.length < Math.pow(2, i)) {
            cuts.push(-1);
        }

        // Sort players into matches
        let new_cuts = cuts.reduce((result, value, index, array) => {
            if (index < array.length / 2) {
                result.push([array[index], array[array.length - index - 1]]);
            }
            return result;
        }, []);

        let front = [];
        let back = [];

        while (new_cuts.length > 0) {
            front.push(new_cuts.shift());
            back.push(new_cuts.shift());
        }

        return [...front, ...back.reverse()].flat();
    }

    onNextRound() {
        if (this.props.topcut_rounds.length === 0) {
            this.props.newState({
                topcut_rounds: [this.newRound(this.firstRoundPairings(this.props.topcut))]
            });

        } else {
            let next = this.props.topcut_rounds[this.props.topcut_rounds.length - 1]
                .map(x => {
                    if (x[0].score !== 0) {
                        return x[0].player.key;
                    }
                    return x[1].player.key;
                });

            if (next.length !== 1) {
                this.props.newState({topcut_rounds: [...this.props.topcut_rounds, this.newRound(next)]});
            } else {
                this.setState({error: `${this.props.players[next[0]].name} is the winner!!`});
            }
        }
    }

    render() {
        let matches = this.props.topcut_rounds.map(
            (x, index) => {
                return <Round
                    onReport={(event) => onRoundReport(event, this.props.topcut_rounds, this.props.newState, "topcut_rounds")}
                    iden={index}
                    matches={x}
                    key={index}
                    hidetie={true}
                />
            }
        );

        return (
            <div>
                <h1>Elimination Matches</h1>
                <div className="buttons">
                    <button onClick={this.onNextRound.bind(this)}>New Round</button>
                    <button onClick={() => onDeleteRound(this.props.topcut_rounds, this.props.newState, "topcut_rounds")}>Delete Round</button>
                </div>
                <div className="wrapper">
                    <div className="matches">
                        {matches}
                    </div>
                </div>
                <p className="error">{this.state.error}</p>

            </div>
        );
    }
}