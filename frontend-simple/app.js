// API endpoint
const API_URL = 'https://waiver.minimaxenergy.com/api/benefitting';

// Get DOM elements
const playersContainer = document.getElementById('players-container');
const loadingEl = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');

// Fetch players data from API
async function fetchPlayers() {
    try {
        loadingEl.style.display = 'block';
        errorMessage.style.display = 'none';

        const response = await fetch(API_URL, { credentials: 'include' });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const playersData = await response.json();
        loadingEl.style.display = 'none';
        displayPlayers(playersData);
    } catch (error) {
        console.error('Error fetching benefitting players:', error);
        loadingEl.style.display = 'none';
        errorMessage.style.display = 'block';
    }
}

// Display injured players
function displayPlayers(playersData) {
    playersContainer.innerHTML = '';
    
    // Iterate over each injured player
    Object.entries(playersData).forEach(([playerName, playerData]) => {
        const playerElement = createPlayerElement(playerName, playerData);
        playersContainer.appendChild(playerElement);
    });
}

// Create a player row element
function createPlayerElement(playerName, playerData) {
    const fragment = document.createDocumentFragment();
    
    // Create main row
    const row = document.createElement('div');
    row.className = 'table-row';
    row.setAttribute('data-player', playerName);
    
    // Calculate if injury is recent (within 3 days)
    const injuryDate = new Date(playerData.time_of_injury.split('T')[0]);
    const threeDaysAgo = new Date();
    threeDaysAgo.setDate(threeDaysAgo.getDate() - 3);
    const isRecentInjury = injuryDate >= threeDaysAgo;
    
    // Disclosure chevron
    const chevron = document.createElement('div');
    chevron.className = 'row-item row-chevron';
    chevron.textContent = '▸';
    row.appendChild(chevron);

    // Player name (PLAYER column)
    const nameDiv = document.createElement('div');
    nameDiv.className = 'row-item col-player player-name';
    nameDiv.textContent = playerName;
    row.appendChild(nameDiv);

    // Stat columns
    const addStatCell = (value) => {
        const cell = document.createElement('div');
        cell.className = 'row-item';
        cell.textContent = Number(value).toFixed(1);
        row.appendChild(cell);
    };
    playerData.stats.forEach(addStatCell);

    // OWN column
    const ownedItem = document.createElement('div');
    ownedItem.className = 'row-item';
    ownedItem.textContent = (playerData.percent_owned != null) ? `${Number(playerData.percent_owned).toFixed(1)}%` : 'N/A';
    row.appendChild(ownedItem);
    
    // Injury status
    const statusDiv = document.createElement('div');
    statusDiv.className = 'row-item injury-status';
    const statusText = document.createElement('div');
    statusText.className = 'status';
    statusText.textContent = playerData.status;
    if (isRecentInjury) {
        statusText.style.fontWeight = '600';
    }
    const dateDiv = document.createElement('div');
    dateDiv.className = 'status-date';
    dateDiv.textContent = new Date(playerData.time_of_injury).toLocaleDateString();
    statusDiv.appendChild(statusText);
    statusDiv.appendChild(dateDiv);
    row.appendChild(statusDiv);
    
    // Click handler to toggle benefiting players
    row.addEventListener('click', function() {
        toggleBenefitingPlayers(row, playerData);
    });
    
    fragment.appendChild(row);
    
    // Create benefiting players container (initially hidden)
    const benefitingContainer = document.createElement('div');
    benefitingContainer.className = 'benefiting-players';
    benefitingContainer.setAttribute('data-player', playerName);
    
    // Add benefiting players with photo, stats and ownership %
    Object.entries(playerData.benefiting_players).forEach(([benefitingPlayer, info]) => {
        const benefitingRow = document.createElement('div');
        benefitingRow.className = 'benefiting-player-row';
        
        // Chevron spacer
        const emptyChevron = document.createElement('div');
        emptyChevron.className = 'row-item row-chevron-spacer';
        emptyChevron.textContent = '';
        benefitingRow.appendChild(emptyChevron);

        // PLAYER column
        const bName = document.createElement('div');
        bName.className = 'row-item col-player benefiting-player-name';
        bName.textContent = benefitingPlayer;
        benefitingRow.appendChild(bName);

        // Stat columns
        info.stats.forEach(val => {
            const c = document.createElement('div');
            c.className = 'benefiting-stat-item';
            c.textContent = Number(val).toFixed(1);
            benefitingRow.appendChild(c);
        });

        // OWN column
        const bOwn = document.createElement('div');
        bOwn.className = 'benefiting-stat-item';
        bOwn.textContent = (info.percent_owned != null) ? `${Number(info.percent_owned).toFixed(1)}%` : 'N/A';
        benefitingRow.appendChild(bOwn);

        // STATUS spacer to align columns
        const statusSpacer = document.createElement('div');
        statusSpacer.className = 'row-item row-status-spacer';
        statusSpacer.textContent = '';
        benefitingRow.appendChild(statusSpacer);
        
        benefitingContainer.appendChild(benefitingRow);
    });
    
    fragment.appendChild(benefitingContainer);
    
    return fragment;
}

// Toggle displaying benefiting players
function toggleBenefitingPlayers(row, playerData) {
    const playerName = row.getAttribute('data-player');
    const benefitingContainer = row.nextElementSibling;
    
    if (benefitingContainer && benefitingContainer.classList.contains('benefiting-players')) {
        benefitingContainer.classList.toggle('show-benefiting-players');
    }
}

// Initialize app on page load
document.addEventListener('DOMContentLoaded', fetchPlayers);
