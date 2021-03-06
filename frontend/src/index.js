import React from "react";
import { BrowserRouter as Router, Route } from 'react-router-dom';
import { render } from "react-dom";
import { config } from "./config";

import { Connect4 } from "./components/Connect4";
import { Header } from "./components/Header";

render(
    <Router>
        <Header/>
        <div className="body">
            <Route path="/connect4_4x4" render={(props) => <Connect4 {...props} url={config.url} name="Connect4_4x4" map_x={4} map_y={4} move="drop" />} />
            <Route path="/connect4_5x4" render={(props) => <Connect4 {...props} url={config.url} name="Connect4_5x4" map_x={5} map_y={4} move="drop" />} />
            <Route path="/connect4_5x5" render={(props) => <Connect4 {...props} url={config.url} name="Connect4_5x5" map_x={5} map_y={5} move="drop" />} />
            <Route path="/connect4_6x5" render={(props) => <Connect4 {...props} url={config.url} name="Connect4_6x5" map_x={6} map_y={5} move="drop" />} />
            <Route path="/tictactoe_3x3" render={(props) => <Connect4 {...props} url={config.url} name="Tictactoe_3x3" map_x={3} map_y={3} move="placement" />} />
            <Route path="/tictactoe_4x4" render={(props) => <Connect4 {...props} url={config.url} name="Tictactoe_4x4" map_x={4} map_y={4} move="placement" />} />
            <div className="game-text">
                <p></p>
            </div>
        </div>
    </Router>
    , window.document.getElementById("app")
);

