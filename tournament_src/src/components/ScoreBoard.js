import React from "react";

export class ScoreBoard extends React.Component {

    state = {
        auto_add: 8,
    }

    onAddPlayer(player) {
        if (!this.props.topcut.includes(player.key)) {
            this.props.newState({topcut: [...this.props.topcut, player.key]});
        }
    }

    onRemovePlayer(player) {
        if (this.props.topcut.includes(player.key)) {
            let filtered = this.props.topcut.filter(key => key !== player.key);
            this.props.newState({topcut: filtered});
        }
    }

    onBulkAdd() {
        let rows = this.props.players.slice(0)
            .sort((a,b) => {return a.sort(b, this.props.players, this.props.rounds)});
        let new_keys = rows.slice(0, this.state.auto_add).map(player => player.key);
        this.props.newState({topcut: new_keys});
    }

    build_row(player) {
        return (
            <tr key={player.key}>
                <td>{player.name}</td>
                <td>{player.score(this.props.rounds)}</td>
                <td>{player.sos(this.props.players, this.props.rounds)}</td>
                <td>{player.seed}</td>
                <td>{player.city}</td>
                <td>{player.character}</td>
                <td><button onClick={() => this.onAddPlayer(player)}>+</button></td>
                <td><button onClick={() => this.onRemovePlayer(player)}>-</button></td>
            </tr>
        );
    }

    onAutoAddChange(event) {
        let value = parseInt(event.target.value);
        this.setState({auto_add: value});
    }

    render() {

        let rows = this.props.players.slice(0)
            .sort((a,b) => {return a.sort(b, this.props.players, this.props.rounds)});

        let added = rows
            .filter(player => this.props.topcut.includes(player.key))
            .map(this.build_row.bind(this));

        let extra = rows
            .filter(player => !this.props.topcut.includes(player.key))
            .map(this.build_row.bind(this));


        return (
            <div>
                <h1>Scores</h1>
                <div className="buttons">
                    <button onClick={() => this.props.newState({topcut: []})}>Reset</button>
                    <button onClick={this.onBulkAdd.bind(this)}>Auto Add</button>
                    <input value={this.state.auto_add} onChange={this.onAutoAddChange.bind(this)} />
                    <input value={this.props.topcut.length} readOnly />
                </div>

                <div className="wrapper">
                    <table className="scoreboard">
                        <thead>
                            <tr>
                                <td>Name</td>
                                <td>Result</td>
                                <td>Sos</td>
                                <td>Seed</td>
                                <td>City</td>
                                <td>Character</td>
                                <td>Add Player</td>
                                <td>Remove Player</td>
                            </tr>
                        </thead>
                        <tbody>
                            {added}
                            <tr className="separator" />
                            {extra}
                        </tbody>
                    </table>
                </div>
            </div>
        );
    }
}