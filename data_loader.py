import json
import csv
import os
from typing import List, Dict, Any

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# CSV file paths
ATS_CSV = os.path.join(DATA_DIR, 'ats_summary.csv')
TPT_CSV = os.path.join(DATA_DIR, 'tpt_summary.csv')
MATCHUP_CSV = os.path.join(DATA_DIR, 'Updated_Player_Matchup_Data.csv')

# In a real app, fetch this from DB or API
MOCK_DATA_FILE = 'mock_nrl_data.json'

def load_matchup_data() -> Dict[str, List[str]]:
    """
    Load matchup data from the CSV file and organize by matchup.
    Returns a dictionary with matchup as key and list of player names in that matchup as value.
    """
    matchups = {}
    
    try:
        with open(MATCHUP_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                matchup = row['Matchup']
                player_name = row['Player Name'].strip()
                team_name = row['Team Name']
                
                if matchup not in matchups:
                    matchups[matchup] = []
                
                matchups[matchup].append({
                    'player_name': player_name,
                    'team_name': team_name
                })
                
        return matchups
    except FileNotFoundError:
        print(f"Error: Matchup file '{MATCHUP_CSV}' not found.")
        return {}
    except Exception as e:
        print(f"Error loading matchup data: {e}")
        return {}

def load_odds_data() -> Dict[str, Dict[str, float]]:
    """
    Load ATS and TPT odds from CSV files.
    Returns a dictionary with player name as key and a dict of their odds as value.
    """
    odds_data = {}
    
    # Load ATS odds
    try:
        with open(ATS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                player_name = row['Player'].strip() if 'Player' in row else ""
                if not player_name:
                    continue
                
                ats_price = row['ATS_prices']
                if ats_price and ats_price != '':
                    if player_name not in odds_data:
                        odds_data[player_name] = {}
                    odds_data[player_name]['ATS'] = float(ats_price)
    except FileNotFoundError:
        print(f"Error: ATS file '{ATS_CSV}' not found.")
    except Exception as e:
        print(f"Error loading ATS data: {e}")
    
    # Load TPT odds
    try:
        with open(TPT_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                player_name = row['Player'].strip() if 'Player' in row else ""
                if not player_name:
                    continue
                
                tpt_price = row['Prices_TwoPlusTry']
                if tpt_price and tpt_price != '':
                    if player_name not in odds_data:
                        odds_data[player_name] = {}
                    odds_data[player_name]['2+'] = float(tpt_price)
    except FileNotFoundError:
        print(f"Error: TPT file '{TPT_CSV}' not found.")
    except Exception as e:
        print(f"Error loading TPT data: {e}")
    
    return odds_data

def load_upcoming_bets_from_csv() -> List[Dict[str, Any]]:
    """Load upcoming bets from the CSV files instead of mock JSON."""
    try:
        matchups = load_matchup_data()
        odds_data = load_odds_data()
        
        # Convert to the format expected by our app
        games_data = []
        
        for matchup, players_info in matchups.items():
            game_bets = []
            
            for player_info in players_info:
                player_name = player_info['player_name']
                
                # Skip players with no name
                if not player_name or player_name.isspace():
                    continue
                
                # Check if we have odds for this player
                if player_name in odds_data:
                    # Add ATS bet if available
                    if 'ATS' in odds_data[player_name]:
                        game_bets.append({
                            "playerId": f"{player_name}_ATS",
                            "playerName": player_name,
                            "market": "ATS",
                            "odds": odds_data[player_name]['ATS'],
                            "team": player_info['team_name']
                        })
                    
                    # Add 2+ bet if available
                    if '2+' in odds_data[player_name]:
                        game_bets.append({
                            "playerId": f"{player_name}_2+",
                            "playerName": player_name,
                            "market": "2+",
                            "odds": odds_data[player_name]['2+'],
                            "team": player_info['team_name']
                        })
            
            # Only add games that have bets
            if game_bets:
                game_id = f"NRL2024_{matchup.replace(' vs ', '_')}"
                games_data.append({
                    "gameId": game_id,
                    "gameDescription": matchup,
                    "bets": game_bets
                })
        
        return games_data
        
    except Exception as e:
        print(f"Error loading data from CSV: {e}")
        return []

def load_upcoming_bets() -> List[Dict[str, Any]]:
    """Loads the available bets for the upcoming round."""
    # Try to load from CSV first
    csv_data = load_upcoming_bets_from_csv()
    if csv_data:
        return csv_data
    
    # Fall back to mock JSON if CSV loading fails
    try:
        # Simulate fetching data - replace with actual data source logic
        with open(MOCK_DATA_FILE, 'r') as f:
            data = json.load(f)
        # Basic validation could go here
        return data
    except FileNotFoundError:
        print(f"Error: Mock data file '{MOCK_DATA_FILE}' not found.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{MOCK_DATA_FILE}'.")
        return []

def get_bets_grouped_by_game() -> Dict[str, List[Dict[str, Any]]]:
    """Groups available bets by gameId."""
    all_games_data = load_upcoming_bets()
    grouped_bets = {}
    for game_data in all_games_data:
        game_id = game_data.get('gameId')
        bets = game_data.get('bets', [])
        game_desc = game_data.get('gameDescription', f'Game {game_id}')
        if game_id and bets:
            # Add game info to each bet for easier access later
            enriched_bets = []
            for bet in bets:
                # Ensure odds are floats
                try:
                    bet['odds'] = float(bet['odds'])
                    bet['gameId'] = game_id  # Add gameId to bet level
                    bet['gameDescription'] = game_desc  # Add gameDesc to bet level
                    enriched_bets.append(bet)
                except (ValueError, TypeError):
                    print(f"Warning: Skipping bet with invalid odds: {bet}")
            if enriched_bets:
                grouped_bets[game_id] = enriched_bets
    return grouped_bets 