import React from "react";
import { config } from "../config";

const urlroot = `${config.url}/connect4`

function Square(props) {
    let name = "grid-square";
    if (props.color) {
        name += " "
        name += props.color
    }

    let inner = "circle ";
    inner += props.value;

    return (
        <button className={name} onClick={props.onClick}>
            <div className={inner}></div>
        </button>
    )
}

function Info(props) {
  let next = props.xNext ? "x" : "o";
  let title = "Next";
  switch (props.endstate) {
    case 1:
      title = "Winner";
      next = "x";
      break;
    case -1:
      next = "o";
      title = "Winner";
      break;
    case 0:
      title = "Tie";
      next = "tie";
      break;
    default:
      // do nothing
  }

  return (
    <div className="game-info">
      <h2>{title}</h2>
      <Square value={next} />
    </div>
  )
}

class Board extends React.Component {
  renderSquare(i, data) {
    let c = data[i];
    var color;

    if (c === 1) {
      color = "x";
    } else if (c === -1) {
      color = "o";
    } else if (c === 0) {
      color = "tie";
    }

    return (
      <Square
        value={this.props.squares[i] === "_" ? null : this.props.squares[i]}
        onClick={() => this.props.onClick(i)}
        color={this.props.hints ? color : null}
      />
    );
  }

  render() {
    var wins = Object.keys(this.props.children).map((key, index) => {
      let child = Array.from(key);
      let parent = this.props.squares;

      let i = 0;
      while (child[i] === parent[i]) {
        i +=1;
      }

      return [i, this.props.children[key].result];
    })

    let obj = {}
    wins.forEach((row) => {
      obj[row[0]] = row[1]
    });

    return (
      <div className="grid">
        <div className="grid-row">
          {this.renderSquare(0, obj)}
          {this.renderSquare(1, obj)}
          {this.renderSquare(2, obj)}
          {this.renderSquare(3, obj)}
        </div>
        <div className="grid-row">
          {this.renderSquare(5, obj)}
          {this.renderSquare(6, obj)}
          {this.renderSquare(7, obj)}
          {this.renderSquare(8, obj)}
        </div>
        <div className="grid-row">
          {this.renderSquare(10, obj)}
          {this.renderSquare(11, obj)}
          {this.renderSquare(12, obj)}
          {this.renderSquare(13, obj)}
        </div>
        <div className="grid-row">
          {this.renderSquare(15, obj)}
          {this.renderSquare(16, obj)}
          {this.renderSquare(17, obj)}
          {this.renderSquare(18, obj)}
        </div>
      </div>
    );
  }
}

export class Connect4 extends React.Component {

  state = {
    gameid: null,
    xNext: true,
    error: false,
    hints: false,
  }

  updateState(url, request) {
    fetch(url, request)
      .then(response => response.json())
      .then(data => this.setState({
        gameid: data.gameid,
        value: data.state.value.result,
        turns: data.state.value.turns,
        current: Array.from(data.state.current),
        children: data.state.children,
        xNext: data.accepted ? !this.state.xNext : this.state.xNext,
        endstate: data.state.endstate,
      }))
      .catch(error => this.setState({error: true}));
  }

  onBoardClick(i) {
    if (this.state.endstate === null) {
      const row = Math.floor(i % 5);
      const url = `${urlroot}/${this.state.gameid}/update`;
      this.updateState(url, {
        method: "post",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          caster: this.state.xNext ? "xPlayer" : "oPlayer",
          target: [row, 0, "map"],
          move: "drop"
        })
      });
    }
  }

  onAiClick(i) {
    if (this.state.endstate === null) {
      const url = `${urlroot}/${this.state.gameid}/update`;
      this.updateState(url, {
        method: "post",
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          caster: this.state.xNext ? "xPlayer" : "oPlayer",
          move: "ai"
        })
      });
    }
  }

  onUndoClick() {
    const url = `${urlroot}/${this.state.gameid}/revert`;
    this.updateState(url);
  }

  onResetClick() {
    const url = `${urlroot}/${this.state.gameid}/reset`;
    this.setState({
        xNext: false,
    });
    this.updateState(url);
  }

  onHintCheck(event) {
    this.setState({
      hints: event.target.checked,
    })
  }

  componentDidMount() {
    const params = new URLSearchParams(this.props.location.search);
    const gameid = params.get("gameid");

    let url;
    if (gameid === null) {
      url = `${urlroot}/new`;
    } else {
      url = `${urlroot}/${gameid}`;
    }

    this.updateState(url)
  }

  render() {
    if (this.state.error) {
      return <div>There is a problem with the server.</div>
    }
    else if (this.state.gameid === null) {
      return <div>Loading</div>;
    }
    else {
      return (
        <div className="game-body">
          <div className="game-board">
            <h1>Connect 4</h1>
            <Board squares={this.state.current} onClick={this.onBoardClick.bind(this)} children={this.state.children} hints={this.state.hints} />
            <div>
              <button className="game-button" onClick={() => this.onUndoClick()}>Undo</button>
              <button className="game-button" onClick={() => this.onResetClick()}>Reset</button>
              <button className="game-button" onClick={() => this.onAiClick()}>AI</button>
              <div>Show Hints <input type="checkbox" onChange={(event) => this.onHintCheck(event)} /></div>
            </div>
          </div>
          <Info xNext={this.state.xNext} endstate={this.state.endstate} />
          {/*
          <div className="results-data">
            <p className="info">Ideal: {this.state.value}</p>
            <p className="info">Turns: {this.state.turns}</p>
            <p className="info">Current: {this.state.endstate}</p>
            <p>Gameid: {this.state.gameid}</p>
          </div>
          */}
        </div>
      );
    }
  }
}
