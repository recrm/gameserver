import React from "react";
import { BrowserRouter as Router, Route } from 'react-router-dom';
import { render } from "react-dom";

import { Connect4 } from "./components/Connect4";
import { Header } from "./components/Header";
import { Sidebar } from "./components/Sidebar";

render(
  <Router>
    <Header/>
    <div className="body">
      <Sidebar/>
      <Route path="/connect4" component={Connect4} />
    </div>
  </Router>
  , window.document.getElementById("app")
);

