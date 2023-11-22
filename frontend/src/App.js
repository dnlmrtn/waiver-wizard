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
        <p>Injured Players:</p>
        <ul>
          {Object.entries(playersData).map(([player, otherPlayers]) => (
            <InjuredPlayer key={player} playerName={player} otherPlayers={otherPlayers}>
              {player}:
            </InjuredPlayer>
          ))}
        </ul>
      </header>
    </div>
  );
}

export default App;
