import React from "react";

function Square(props) {
    let name = "grid-square";
    if (props.color) {
        name += " "
        name += props.color
    }

    let inner = "circle ";
    inner += props.value;

    return (
        <div disabled={props.disable} className={name} onClick={props.onClick}>
            <div className="grid-square-inner">
                <div className={inner}></div>
            </div>
        </div>
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
      <h1>{props.thinking ? "Thinking" : title}</h1>
      <div className="grid">
          <Square value={next} />
      </div>
    </div>
  )
}

class Board extends React.Component {
  renderSquare(i, data) {
    let c = data[i];
    var color;

    if (c === 1) {
      color = "win";
    } else if (c === -1) {
      color = "lose";
    } else if (c === 0) {
      color = "tie";
    }

    return (
      <Square
        value={this.props.squares[i] === "_" ? null : this.props.squares[i]}
        onClick={() => this.props.onClick(i)}
        color={this.props.hints ? color : null}
        disable={this.props.thinking}
        key={i}
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

      return [i, this.props.children[key]];
    })

    let obj = {}
    wins.forEach((row) => {
      obj[row[0]] = row[1]
    });

    let rows = [];
    let i = 0;
    for (let k = 0; k < this.props.map_y; k++) {
      let cols = [];
      for (let j = 0; j < this.props.map_x; j++) {
        cols.push(this.renderSquare(i++, obj))
      }
      rows.push(<div className="grid-row" key={k}>{cols}</div>)
      i++;
    }

    return (
      <div className="grid">
        {rows}
      </div>
    );
  }
}

export class Connect4 extends React.Component {

  state = {
    gameid: null,
    xNext: true,
    error: false,
    hints: "none",
    thinking: false,
  }

  updateState(url, request) {
    this.setState({thinking: true});
    fetch(url, request)
      .then(response => {
//         console.log(response.text())
        return response.json();
      })
      .then(data => {
        if (data.message !== undefined) {
          console.error(data.message);
          if (data.message === "Game id not found") {
            this.setState({xNext: true});
            this.updateState(`${this.props.url}/${this.props.name}/new/${this.state.hints}`);
          } else  {
            this.setState({error:true, thinking: false});
          }
        } else {
          this.setState({
            gameid: data.gameid,
            current: Array.from(data.state.current),
            children: data.state.children,
            xNext: data.accepted ? !this.state.xNext : this.state.xNext,
            endstate: data.state.endstate,
            thinking: false,
          });
        }
      })
      .catch((error) => {
        console.log(error);
        this.setState({"error": true});
    })
  }

  onBoardClick(i) {
    if (this.state.endstate === null) {
      const row = i % (this.props.map_x + 1);
      const col = (i - row) / (this.props.map_x + 1)

      let formData = new FormData();
      formData.append("caster", this.state.xNext ? "xPlayer" : "oPlayer");
      formData.append("move", this.props.move);
      formData.append("target", [row, col, "map"]);

      const url = `${this.props.url}/${this.props.name}/${this.state.gameid}/update/${this.state.hints}`;
      this.updateState(url, {
        method: "post",
        body: formData,
      });
    }
  }

  onAiClick(i) {
    if (this.state.endstate === null) {
      let formData = new FormData();
      formData.append("caster", this.state.xNext ? "xPlayer" : "oPlayer");
      formData.append("move", "ai");
      formData.append("target", this.props.move);

      const url = `${this.props.url}/${this.props.name}/${this.state.gameid}/update/${this.state.hints}`;
      this.updateState(url, {
        method: "post",
        body: formData
      });
    }
  }

  onUndoClick() {
    const url = `${this.props.url}/${this.props.name}/${this.state.gameid}/revert/${this.state.hints}`;
    this.updateState(url);
  }

  onResetClick() {
    const url = `${this.props.url}/${this.props.name}/${this.state.gameid}/reset/none`;
    this.setState({xNext: false, hints: "none"});
    this.updateState(url);
  }

  onHintCheck(event) {
    const hints = event.target.checked ? "children" : "none";
    this.setState({hints: hints});
    const url = `${this.props.url}/${this.props.name}/${this.state.gameid}/${hints}`;
    this.updateState(url);
  }

  componentDidMount() {
    const params = new URLSearchParams(this.props.location.search);
    const gameid = params.get("gameid");

    let url;
    if (gameid === null) {
      url = `${this.props.url}/${this.props.name}/new/${this.state.hints}`;
    } else {
      url = `${this.props.url}/${this.props.name}/${gameid}`;
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
                    <h1>{this.props.name}</h1>
                    <Board
                        squares={this.state.current}
                        onClick={this.onBoardClick.bind(this)}
                        children={this.state.children}
                        hints={this.state.hints}
                        thinking={this.state.thinking}
                        map_x={this.props.map_x}
                        map_y={this.props.map_y}
                        />
                    <div className="game-controls">
                        <button disabled={this.state.thinking} className="game-button" onClick={() => this.onUndoClick()}>Undo</button>
                        <button disabled={this.state.thinking} className="game-button" onClick={() => this.onResetClick()}>Reset</button>
                        <button disabled={this.state.thinking} className="game-button" onClick={() => this.onAiClick()}>AI</button>
                        <div>Show Hints <input disabled={this.state.thinking}
                                            type="checkbox"
                                            checked={(this.state.hints === "children")}
                                            onChange={(event) => this.onHintCheck(event)}
                                            /></div>
                    </div>
                </div>
                <Info xNext={this.state.xNext} endstate={this.state.endstate} thinking={this.state.thinking} />
            </div>
      );
    }
  }
}
