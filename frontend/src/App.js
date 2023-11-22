import React, { useState, useEffect } from 'react';
import './App.css';
import './InjuredPlayer.js'
import InjuredPlayer from './InjuredPlayer.js';

function App() {
  // Rename the state variable for clarity
  const [playersData, setPlayersData] = useState({});

  useEffect(() => {
    // Fetch data from the Django backend
    fetch('http://0.0.0.0:8000/benefitting/')
      .then(res => res.json())
      .then(data => {
        // Update state with the fetched data
        setPlayersData(data);
      });
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <p>Welcome to Waiver Wizard!</p>
        <p className='subtitle'>See the list of siginificant fantasy players who are not playing tonight, and click on them to see players with role increases :)</p>
      
        <ul >
          {Object.entries(playersData).map(([player, otherPlayers]) => (
            <li>
            <InjuredPlayer key={player} playerName={player} otherPlayers={otherPlayers}>
              {player}:
            </InjuredPlayer>
            </li>
          ))}
        </ul>
        </header>
        <p className='subtitle'>Player stats are updated every 10 minutes between 5:30pm to 10pm EST, and every morning at 7am.</p>

    </div>
  );
}

export default App;
