import React, { useState } from 'react';
import '../static/InjuredPlayer.css';

const InjuredPlayer = ({ playerName, playerData }) => {
  const [showBenefitingPlayers, setShowBenefitingPlayers] = useState(false);

  const toggleBenefitingPlayers = () => {
    setShowBenefitingPlayers(!showBenefitingPlayers);
  };
  console.log(playerData.time_of_injury)
  const injuryDate = new Date(playerData.time_of_injury.split('T')[0]);

  // Create a new Date object for 3 days ago
  const threeDaysAgo = new Date();
  threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);


  return (
    <>
      <div className="table-row" onClick={toggleBenefitingPlayers}>
        <div className="player-image"><img src={playerData.photo_url} alt={playerName} /></div>
        <div className='player-data-container'>
          <div className="player-name">{playerName}</div>
          <div className='stat-line'>
            {playerData.stats.map((stat, index) => (
              <div key={index} className="row-item">{stat}</div>
            ))}
            <div className="row-item">{playerData.percent_owned != null ? `${Number(playerData.percent_owned).toFixed(1)}%` : 'N/A'}</div>
          </div>
        </div >
        <div className="injury-status">
          <span className="status" style={{ color: 'red', fontWeight: injuryDate >= threeDaysAgo ? "bold" : "" }}>{playerData.status}<br /><div style={{ color: '#d9dadb' }}>{new Date(playerData.time_of_injury).toLocaleDateString()}</div></span>
        </div>

      </div>

      {/* Add 'show-benefiting-players' class conditionally based on 'showBenefitingPlayers' state */}
      <div className={`benefiting-players ${showBenefitingPlayers ? "show-benefiting-players" : ""}`}>
        {Object.entries(playerData.benefiting_players).map(([benefitingPlayer, info]) => (
          <div key={benefitingPlayer} className="benefiting-player-row">
            <div className="player-image"><img src={info.photo_url} alt={benefitingPlayer} /></div>
            <div className="benefiting-player-item">{benefitingPlayer}</div>
            {info.stats.map((stat, index) => (
              <div key={index} className="benefiting-player-item">{stat}</div>
            ))}
            <div className="benefiting-player-item">{info.percent_owned != null ? `${Number(info.percent_owned).toFixed(1)}%` : 'N/A'}</div>
          </div>
        ))}
      </div>
    </>
  );
};

export default InjuredPlayer;
