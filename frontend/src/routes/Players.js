import React from 'react';
import InjuredPlayer from '../components/InjuredPlayer';
import Footer from '../components/Footer.js';
import { useBenefittingPlayers } from '../hooks/useBenefittingPlayers';

import '../static/InjuredPlayer.css';
import '../static/index.css';
import '../static/App.css';

function Players() {
  const { playersData, error } = useBenefittingPlayers();

  if (error) {
    return <div className="App">Failed to load players data.</div>;
  }

  return (
    <div className="App">
      <div className="content">
        <header className="App-header">Waiver Wizard</header>
        <div className="subtitle">
          Displaying injured NBA players, click one to see who benefits.
        </div>
        <div className="table-container">
          <div className="table">
            <div className="table-header">
              <div className="header-item"></div>
              <div className="header-item">PTS</div>
              <div className="header-item">REB</div>
              <div className="header-item">AST</div>
              <div className="header-item">STL</div>
              <div className="header-item">BLK</div>
              <div className="header-item">TOV</div>
              <div className="header-item">Status</div>
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

