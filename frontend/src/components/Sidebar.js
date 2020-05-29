import React from "react";
import { Link } from 'react-router-dom';

export const Sidebar = (props) => {
  return (
    <nav className="sidebar">
      <h3>Games</h3>
      <ul className="nav-links">
        <li><h4>Connect4</h4></li>
        <Link to="/connect4_4x4">
          <li>4 by 4</li>
        </Link>
        <Link to="/connect4_5x4">
          <li>5 by 4</li>
        </Link>
        <Link to="/connect4_5x5">
          <li>5 by 5</li>
        </Link>
      </ul>
    </nav>
  );
}