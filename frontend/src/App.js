import React, { useState, useEffect } from 'react';
import './App.css';
import './InjuredPlayer.js'
import InjuredPlayer from './InjuredPlayer.js';

function App() {
  const [playersData, setPlayersData] = useState({ benefitting_players: {}, time_of_injury: {} });

  useEffect(() => {
    fetch('http://0.0.0.0:8000/benefitting/')
      .then(res => res.json())
      .then(data => {
        setPlayersData(data);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <p>Welcome to Waiver Wizard!</p>
        <p className='subtitle'>See the list of significant fantasy players who are not playing tonight, and click on them to see players with role increases :)</p>
      
        <ul>
          {Object.entries(playersData.benefitting_players).map(([player, otherPlayers]) => (
            <li key={player}>
              <InjuredPlayer 
                playerName={player} 
                otherPlayers={otherPlayers} 
                timeOfInjury={playersData.time_of_injury[player]} 
              />
            </li>
          ))}
        </ul>
      </header>
      <p className='subtitle'>Player stats are updated every 10 minutes between 5:30pm to 10pm EST, and every morning at 7am.</p>
    </div>
  );
}

export default App;
