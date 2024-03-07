const socket = io('{{ url }}');

function updateScores(data) {
    // Update score table
    const scoreTable = document.getElementById('scores');
    scoreTable.innerHTML = '<tr><th>Name</th><th>Score</th><th>Rounds</th><th>Rate</th></tr>';

    console.log(data);
    var sortedPlayers = Object.keys(data.score);
    sortedPlayers.sort (function(a, b) {
        const aScore = data.score[a];
        const aParticipation = data.participation[a];
        const bScore = data.score[b];
        const bParticipation = data.participation[b];
        const aRate=aScore/aParticipation;
        const bRate=bScore/bParticipation;
        if (aRate < bRate) {
            return 1;
        } else if (aRate > bRate) {
            return -1;
        }
        return 0;
    });

    for (var i = 0; i < sortedPlayers.length; i++) {
        const name = sortedPlayers[i];
        const playerScore = data.score[name];
        const playerParticipation = data.participation[name];
        const row = scoreTable.insertRow();
        const playerRate=playerScore/playerParticipation;
        row.insertCell().textContent = name;
        row.insertCell().textContent = playerScore;
        row.insertCell().textContent = playerParticipation;
        row.insertCell().textContent = playerRate;
        if (data.correctPlayers && data.correct_players.includes(name)) {
          row.style.backgroundColor = 'lime';
        }
    }
    document.getElementById('scoreContainer').appendChild(scoreTable);
}
