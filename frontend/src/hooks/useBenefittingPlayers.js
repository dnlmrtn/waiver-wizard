import { useEffect, useState } from 'react';
import axios from 'axios';

export function useBenefittingPlayers() {
  const [playersData, setPlayersData] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPlayers = async () => {
      try {
        const baseUrl = process.env.REACT_APP_SITE_URL || '';
        const res = await axios.get(`waiver.minimaxenergy.com/api/benefitting`, {
          withCredentials: true,
        });
        setPlayersData(res.data);
      } catch (err) {
        console.error('Error fetching benefitting players:', err);
        setError(err);
      }
    };

    fetchPlayers();
  }, []);

  return { playersData, error };
}

