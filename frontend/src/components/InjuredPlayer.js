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
        <div className="row-item"><img src={playerData.photo_url} alt={playerName} /></div>
        <div className="row-item">{playerName}</div>
        {playerData.stats.map((stat, index) => (
          <div key={index} className="row-item">{stat}</div>
        ))}
        <div className="row-item">
          <span className="status" style={{ color: 'red', fontWeight: injuryDate >= threeDaysAgo ? "bold" : "" }}>{playerData.status}<br /><div style={{ color: '#d9dadb' }}>{new Date(playerData.time_of_injury).toLocaleDateString()}</div></span>
        </div>
      </div >

      {showBenefitingPlayers && (
        <div className="benefiting-players">
          {Object.entries(playerData.benefiting_players).map(([benefitingPlayer, stats]) => (
            <div key={benefitingPlayer} className="benefiting-player-row">

              <div className="benefiting-player-item">{benefitingPlayer}</div>
              {stats.map((stat, index) => (
                <div key={index} className="benefiting-player-item">{stat}</div>
              ))}

            </div>
          ))}
        </div>
      )}
    </>
  );
};

export default InjuredPlayer;