function randint(min, max) {
    min = Math.ceil(min);
    max = Math.floor(max);
    return Math.floor(Math.random() * (max - min + 1)) + min;
}

function handleChange(self, event) {
    if (event.target.name === "seed") {
        event.target.value = parseInt(event.target.value);
    }

    self[event.target.name] = event.target.value;
    self.update();
}

function score(self, rounds) {
    return rounds.reduce((a, round) => {
        return a + round.reduce((a, match) => {
            let score = 0;
            match.forEach((player) => {
                if (player.player.key === self.key) {
                    score += player.score;
                }
            });
            return a + score;
        }, 0);
    }, 0);
}

function opponents(self, rounds) {
    // Return an array of opponents we have already faced.
    return rounds.reduce((a, round) => {
        return a.concat(round.reduce((a, match) => {
            let [first, second] = match;

            if (first.player.key === self.key) {
                a.push(second.player.key);
            } else if (second.player.key === self.key) {
                a.push(first.player.key);
            }
            return a;
        }, []));
    }, []);
}

function sos(self, players, rounds) {
    return self.opponents(rounds).reduce((total, key) => {
        if (key !== -1) {
            total += players[key].score(rounds);
        }
        return total
    }, 0);
}

function sort(self, b, players, matches) {
    let scorea = self.score(matches);
    let scoreb = b.score(matches);

    if (scorea === scoreb) {
        let sosa = self.sos(players, matches);
        let sosb = b.sos(players, matches);
        if (sosa === sosb) {
            return b.seed - self.seed;
        }
        return sosb - sosa;
    }
    return scoreb - scorea;
}

export function restorePlayer(self, update) {
    self.update = update
    self.handleChange = (...a) => handleChange(self, ...a)
    self.score = (...a) => score(self, ...a)
    self.opponents = (...a) => opponents(self, ...a)
    self.sos = (...a) => sos(self, ...a)
    self.sort = (...a) => sort(self, ...a)
}

export function player (key, update) {
    let self = {
        name: key,
        city: "",
        character: "",
        seed: randint(0, 100),
        key: key,
    }

    restorePlayer(self, update);
    return self;
}

export const by_player = player(-1)
by_player.name = "BY"