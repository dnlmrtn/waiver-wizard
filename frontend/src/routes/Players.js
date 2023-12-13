import React, { useState, useEffect } from 'react';

import InjuredPlayer from '../components/InjuredPlayer';

import '../static/InjuredPlayer.css'
import '../static/index.css'
import '../static/App.css'

function Players() {
  const [playersData, setPlayersData] = useState({});

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
        <p className='subtitle'>See the list of significant players who are not playing tonight, click them to see players with role increases.</p>
      </header>
      <div className='table'>
        <div className='table-header'>
          <div className='header-item'></div>
          <div className='header-item'>Name</div>
          <div className='header-item'>PTS</div>
          <div className='header-item'>REB</div>
          <div className='header-item'>AST</div>
          <div className='header-item'>STL</div>
          <div className='header-item'>BLK</div>
          <div className='header-item'>TOV</div>
          <div className='header-item'>Status</div>
        </div>
        {Object.entries(playersData).map(([playerName, playerData]) => (
          <InjuredPlayer
            key={playerName}
            playerName={playerName}
            playerData={playerData}
          />
        ))}
      </div>
      <p className='subtitle'>Player status is updated every 10 minutes between 4:30pm to 10pm EST. Keep an eye out for changes.</p>
    </div>
  );
}

export default Players;