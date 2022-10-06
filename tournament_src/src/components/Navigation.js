import React from "react";
import { Timer } from "./Timer";

export const Navigation = (props) => {
    return (
        <div className="header">
            <img className="logo" src={"logo.png"} alt="" />
            <div className="columns">
                <div className="buttons">
                    <button onClick={() => props.newState({page: "players"})}>People</button>
                    <button onClick={() => props.newState({page: "matches"})}>Swiss</button>
                    <button onClick={() => props.newState({page: "data"})}>Export</button>
                </div>
                <div className="buttons">
                    <button onClick={() => props.newState({page: "scores"})}>Scores</button>
                    <button onClick={() => props.newState({page: "topcut"})}>Elimination</button>
                    <button onClick={() => props.newState({page: "enter"})}>Load</button>
                </div>
            </div>

            <div className="attribution">
                <p>Programmed by Ryan Chartier</p>
                <p>Please report bugs on <a href="https://github.com/recrm/openTournament">github</a></p>
            </div>
            <Timer />
        </div>
    );
}