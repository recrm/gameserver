import React from "react";
import { BrowserRouter as Router, Route } from 'react-router-dom';
import { render } from "react-dom";
import { config } from "./config";

import { Connect4 } from "./components/Connect4";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";

render(
  <Router>
    <Header/>
    <div className="body">
      <Sidebar/>
      <Route path="/connect4_4x4" render={(props) => <Connect4 {...props} urlroot={`${config.url}/Connect4_4x4`} map_x = {4} map_y = {4} move="drop" />} />
      <Route path="/connect4_5x4" render={(props) => <Connect4 {...props} urlroot={`${config.url}/Connect4_5x4`} map_x = {5} map_y = {4} move="drop" />} />
      <Route path="/connect4_5x5" render={(props) => <Connect4 {...props} urlroot={`${config.url}/Connect4_5x5`} map_x = {5} map_y = {5} move="drop" />} />
      <Route path="/tictactoe_3x3" render={(props) => <Connect4 {...props} urlroot={`${config.url}/Tictactoe_3x3`} map_x = {3} map_y = {3} move="placement" />} />
      <Route path="/tictactoe_4x4" render={(props) => <Connect4 {...props} urlroot={`${config.url}/Tictactoe_4x4`} map_x = {4} map_y = {4} move="placement" />} />
    </div>
  </Router>
  , window.document.getElementById("app")
);

