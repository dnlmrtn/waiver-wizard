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
      <div className='content'>
        <header className="App-header">
          Welcome to waiver wizard!
        </header>
        <subtitle className="subtitle">
          Displaying injured nba players, click one to see who benefits.
        </subtitle>


        <div className='table-container'>
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
        </div>
        <p className='subtitle'>Player status is updated every 10 minutes between 4:30pm to 10pm EST. Keep an eye out for changes.</p>
      </div>
    </div>
  );
}

export default Players;
