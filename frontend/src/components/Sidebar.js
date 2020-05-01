import React from "react";
import { Link } from 'react-router-dom';

export const Sidebar = (props) => {
  return (
    <nav className="sidebar">
      <h3>Games</h3>
      <ul className="nav-links">
        <Link to="/connect4">
          <li>Connect4</li>
        </Link>
      </ul>
    </nav>
  );
}