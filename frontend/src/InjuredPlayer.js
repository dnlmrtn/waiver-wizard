import React, { useState } from 'react';

const InjuredPlayer = ({ playerName, otherPlayers, onClick }) => {
  const [showPopups, setShowPopups] = useState(false);

  const handleClick = () => {
    // Toggle the state to show/hide popups
    setShowPopups(!showPopups);
  };

  return (
    <div className="player-bubble">
      <button onClick={handleClick}>{playerName}</button>
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
