import React, { useState } from 'react';
import "./InjuredPlayer.css"

const InjuredPlayer = ({ playerName, otherPlayers, onClick }) => {
  const [showPopups, setShowPopups] = useState(false);

  const handleClick = () => {
    // Toggle the state to show/hide popups
    setShowPopups(!showPopups);
  };

  return (
    <div className="player-bubble">
      <div className='injured-button' onClick={handleClick}>{playerName}</div>
      {showPopups && (
        <div className="popups">
          {otherPlayers.map((otherPlayer, index) => (
            <div className="popup" key={index}>
              {otherPlayer}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default InjuredPlayer;
