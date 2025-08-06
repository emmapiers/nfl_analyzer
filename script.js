// Example matchups — update weekly!
const matchups = [
    { teamA: "49ers", teamB: "Cowboys", teamARank: 2, teamBRank: 5 },
    { teamA: "Eagles", teamB: "Giants", teamARank: 1, teamBRank: 10 },
    { teamA: "Chiefs", teamB: "Bills", teamARank: 3, teamBRank: 4 },
    { teamA: "Ravens", teamB: "Bengals", teamARank: 6, teamBRank: 9 },
  ];
  
  const grid = document.getElementById("matchup-grid");
  
  matchups.forEach(matchup => {
    const card = document.createElement("div");
    card.className = "matchup-card";
    card.innerHTML = `
      <h3>${matchup.teamA} 🆚 ${matchup.teamB}</h3>
      <p><strong>${matchup.teamA} Rank:</strong> ${matchup.teamARank}</p>
      <p><strong>${matchup.teamB} Rank:</strong> ${matchup.teamBRank}</p>
    `;
    grid.appendChild(card);
  });
  