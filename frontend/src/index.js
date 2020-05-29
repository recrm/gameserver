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
      <Route path="/connect4_4x4" render={(props) => <Connect4 {...props} urlroot={`${config.url}/connect4_4x4`} map_x = {4} map_y = {4} />} />
      <Route path="/connect4_5x4" render={(props) => <Connect4 {...props} urlroot={`${config.url}/connect4_5x4`} map_x = {5} map_y = {4} />} />
      <Route path="/connect4_5x5" render={(props) => <Connect4 {...props} urlroot={`${config.url}/connect4_5x5`} map_x = {5} map_y = {5} />} />
    </div>
  </Router>
  , window.document.getElementById("app")
);

