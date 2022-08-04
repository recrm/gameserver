import React from "react";

(function() {
  window.accurateInterval = function(time, fn) {
    let cancel, nextAt, timeout, wrapper, _ref;
    nextAt = new Date().getTime() + time;
    timeout = null;
    if (typeof time === 'function') {
        _ref = [time, fn];
        fn = _ref[0];
        time = _ref[1];
    }

    wrapper = function() {
      nextAt += time;
      timeout = setTimeout(wrapper, nextAt - new Date().getTime());
      return fn();
    };
    cancel = function() {
      return clearTimeout(timeout);
    };
    timeout = setTimeout(wrapper, nextAt - new Date().getTime());
    return {
      cancel: cancel
    };
  };
}).call(this);

export class Timer extends React.Component {

    state = {
        seconds: 0,
        hours: 0,
        minutes: 0,
        remaining_seconds: 0,
        remaining_hours: 0,
        remaining_minutes: 0,
        stop_timer: true,
    }

    onTimeChange(event) {
        let obj = {}
        obj[event.target.name] = event.target.value;
        this.setState(obj);
    }

    onGo() {
        this.setState({
            remaining_seconds: this.state.seconds,
            remaining_hours: this.state.hours,
            remaining_minutes: this.state.minutes,
            stop_timer: false,
        })
    }

    componentDidMount() {
        this.myInterval = window.accurateInterval(1000, () => {
            let { remaining_seconds, remaining_minutes, remaining_hours } = this.state;
            let decrement_minutes = false;
            let decrement_hours = false;
            let stop_timer = false;

            if (remaining_seconds > 0) {
                remaining_seconds -= 1;
            } else {
                remaining_seconds = 59;
                decrement_minutes = true;
            }

            if (decrement_minutes) {
                if (remaining_minutes > 0) {
                    remaining_minutes -= 1;
                } else {
                    remaining_minutes = 59;
                    decrement_hours = true;
                }
            }

            if (decrement_hours) {
                if (remaining_hours > 0) {
                    remaining_hours -= 1;
                } else {
                    stop_timer = true;
                }
            }

            if (stop_timer) {
                this.setState({
                    remaining_seconds: 0,
                    remaining_minutes: 0,
                    remaining_hours: 0,
                    stop_timer,
                })
            } else {
                this.setState({
                    remaining_seconds,
                    remaining_minutes,
                    remaining_hours,
                    stop_timer,
                })
            }
        });
    }

    render() {
        const name = this.state.stop_timer ? "timer-off" : "timer-on"


        return (
            <div className="timer">
                <div className={name}>
                    {this.state.remaining_hours.toString().padStart(2,'0')}:{this.state.remaining_minutes.toString().padStart(2,'0')}:{this.state.remaining_seconds.toString().padStart(2,'0')}
                </div>

                <div className="timer-controls">
                    <input name="hours" type="number" min="0" value={this.state.hours} onChange={this.onTimeChange.bind(this)} />
                    <input name="minutes" type="number" min="0" max="59" value={this.state.minutes} onChange={this.onTimeChange.bind(this)} />
                    <input name="seconds" type="number" min="0" max="59" value={this.state.seconds} onChange={this.onTimeChange.bind(this)} />
                    <button onClick={this.onGo.bind(this)}>Start</button>
                </div>
            </div>
        )
    }
}
