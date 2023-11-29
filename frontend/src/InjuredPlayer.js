import React, { useState } from 'react';
import "./InjuredPlayer.css";

const InjuredPlayer = ({ playerName, otherPlayers, timeOfInjury }) => {
  const [showPopups, setShowPopups] = useState(false);

  const handleClick = () => {
    setShowPopups(!showPopups);
  };

  const formatDate = (dateString) => {
    const options = { month: 'long', day: 'numeric' }; // Removed the year
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <div className="player-bubble">
      <div className='injured-button' onClick={handleClick}>
        {playerName}
        <div className="injury-date">{formatDate(timeOfInjury)}</div>
      </div>
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
