import { useEffect, useState } from 'react';

export function useBenefittingPlayers() {
  const [playersData, setPlayersData] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    // Dummy hardcoded data to preview UI changes without backend
    const dummyData = {
      "LeBron James": {
        photo_url: "https://s.yimg.com/i/us/sp/v/nba_cutout/players_l/20240222/3704.png",
        stats: [25.4, 7.8, 8.1, 1.2, 0.8, 3.4],
        percent_owned: 97.2,
        benefiting_players: {
          "D'Angelo Russell": {
            photo_url: "https://s.yimg.com/i/us/sp/v/nba_cutout/players_l/20240222/5219.png",
            stats: [18.2, 3.1, 6.4, 1.1, 0.3, 2.6],
            percent_owned: 52.3
          },
          "Austin Reaves": {
            photo_url: "https://s.yimg.com/i/us/sp/v/nba_cutout/players_l/20240222/6573.png",
            stats: [15.6, 4.4, 5.2, 0.9, 0.3, 1.8],
            percent_owned: 64.9
          },
          "Rui Hachimura": {
            photo_url: "https://s.yimg.com/i/us/sp/v/nba_cutout/players_l/20240222/6071.png",
            stats: [13.3, 5.0, 1.2, 0.8, 0.4, 1.1],
            percent_owned: 31.1
          }
        },
        time_of_injury: "2025-10-25T12:34:56Z",
        status: "INJ"
      },
      "Devin Booker": {
        photo_url: "https://s.yimg.com/i/us/sp/v/nba_cutout/players_l/20240222/5415.png",
        stats: [27.9, 4.6, 6.7, 1.1, 0.4, 2.9],
        percent_owned: 98.4,
        benefiting_players: {
          "Grayson Allen": {
            photo_url: "https://s.yimg.com/i/us/sp/v/nba_cutout/players_l/20240222/5697.png",
            stats: [13.4, 3.7, 3.1, 1.0, 0.2, 1.1],
            percent_owned: 48.7
          },
          "Eric Gordon": {
            photo_url: "https://s.yimg.com/i/us/sp/v/nba_cutout/players_l/20240222/4244.png",
            stats: [11.8, 2.2, 2.7, 0.7, 0.3, 1.5],
            percent_owned: 22.5
          }
        },
        time_of_injury: "2025-10-27T08:15:00Z",
        status: "O"
      }
    };

    // Simulate async load
    const timer = setTimeout(() => {
      setPlayersData(dummyData);
      setError(null);
    }, 300);

    return () => clearTimeout(timer);
  }, []);

  return { playersData, error };
}

