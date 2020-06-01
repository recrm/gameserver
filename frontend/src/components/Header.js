import React from "react";
import { Link } from 'react-router-dom';

export const Header = (props) => {
    return (
        <div className="header">
            <div className="sitename">
                <h1>Ak-Rc Games</h1>
            </div>
            <div className="sidebar">
                <ul>
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
                <ul>
                    <li><h4>TicTacToe</h4></li>
                    <Link to="/tictactoe_3x3">
                        <li>3 by 3</li>
                    </Link>
                    <Link to="/tictactoe_4x4">
                        <li>4 by 4</li>
                    </Link>
                </ul>
            </div>
        </div>
    );
}