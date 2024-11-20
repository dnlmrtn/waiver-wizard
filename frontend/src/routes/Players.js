import React, { useState, useEffect } from 'react';

import InjuredPlayer from '../components/InjuredPlayer';
import axios from 'axios';

import '../static/InjuredPlayer.css'
import '../static/index.css'
import '../static/App.css'

import Footer from '../components/Footer.js';

function Players() {
  const [playersData, setPlayersData] = useState({});
  const apiBaseUrl = process.env.SITE_URL;

  useEffect(() => {
        axios
            .get('http://localhost:8000/api/benefitting', { withCredentials: true })
            .then((res) => {
                setPlayersData(res.data);
            })
            .catch((error) => {
                console.error('Error fetching flow data:', error);
            });
    }, []);

  console.log(playersData)

  return (
    <div className="App">
      <div className='content'>
        <header className="App-header">
          Waiver Wizard
        </header>
        <div className="subtitle">
          Displaying injured nba players, click one to see who benefits.
        </div>
        <div className='table-container'>
          <div className='table'>
            <div className='table-header'>
              <div className='header-item'></div>
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
        <Footer />
      </div>

    </div>
  );
}

export default Players;
