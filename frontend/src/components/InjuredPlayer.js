import React, { useState } from 'react';
import '../static/InjuredPlayer.css';

const InjuredPlayer = ({ playerName, playerData }) => {
  const [showBenefitingPlayers, setShowBenefitingPlayers] = useState(false);

  const toggleBenefitingPlayers = () => {
    setShowBenefitingPlayers(!showBenefitingPlayers);
  };

  return (
    <>
      <div className="table-row" onClick={toggleBenefitingPlayers}>
        <div className="row-item"><img src={playerData.photo_url} alt={playerName} /></div>
        <div className="row-item">{playerName}</div>
        {playerData.stats.map((stat, index) => (
          <div key={index} className="row-item">{stat}</div>
        ))}
        <div className="row-item">
          <span className="status" style={{ color: 'red' }}>{playerData.status}<br /><div style={{ color: '#222222' }}>{new Date(playerData.time_of_injury).toLocaleDateString()}</div></span>
        </div>
      </div >
      {showBenefitingPlayers && (
        <div className="benefiting-players">
          {Object.entries(playerData.benefiting_players).map(([benefitingPlayer, stats]) => (
            <div key={benefitingPlayer} className="benefiting-player-row">
              <div className="benefiting-player-item empty"></div> {/* Empty for alignment */}
              <div className="benefiting-player-item">{benefitingPlayer}</div>
              {stats.map((stat, index) => (
                <div key={index} className="benefiting-player-item">{stat}</div>
              ))}
              <div className="benefiting-player-item empty"></div> {/* Empty for alignment */}
            </div>
          ))}
        </div>
      )}
    </>
  );
};

export default InjuredPlayer;