import json
import csv
import os
from typing import List, Dict, Any

# Path to the data directory
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

# NRL CSV file paths
ATS_CSV = os.path.join(DATA_DIR, 'ats_summary.csv')
TPT_CSV = os.path.join(DATA_DIR, 'tpt_summary.csv')
MATCHUP_CSV = os.path.join(DATA_DIR, 'Updated_Player_Matchup_Data.csv')

# AFL CSV file paths
AFL_2GS_CSV = os.path.join(DATA_DIR, '2gs_summary.csv')
AFL_AGS_CSV = os.path.join(DATA_DIR, 'ags_summary.csv')
AFL_MATCHUP_CSV = os.path.join(DATA_DIR, 'AFL_Upcoming_Matchup.csv')

# In a real app, fetch this from DB or API
MOCK_DATA_FILE = 'mock_nrl_data.json'

def load_nrl_matchup_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load NRL matchup data from the CSV file and organize by matchup.
    Returns a dictionary with matchup as key and list of player info in that matchup as value.
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
        print(f"Error: NRL Matchup file '{MATCHUP_CSV}' not found.")
        return {}
    except Exception as e:
        print(f"Error loading NRL matchup data: {e}")
        return {}

def load_afl_matchup_data() -> Dict[str, List[Dict[str, Any]]]:
    """
    Load AFL matchup data from the CSV file and organize by matchup.
    Returns a dictionary with matchup as key and list of player info in that matchup as value.
    """
    matchups = {}
    
    try:
        with open(AFL_MATCHUP_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                matchup = row['matchup']
                player_name = row['Player'].strip()
                team_name = row['Team']
                
                if matchup not in matchups:
                    matchups[matchup] = []
                
                matchups[matchup].append({
                    'player_name': player_name,
                    'team_name': team_name
                })
                
        return matchups
    except FileNotFoundError:
        print(f"Error: AFL Matchup file '{AFL_MATCHUP_CSV}' not found.")
        return {}
    except Exception as e:
        print(f"Error loading AFL matchup data: {e}")
        return {}

def load_nrl_odds_data() -> Dict[str, Dict[str, float]]:
    """
    Load NRL ATS and TPT odds from CSV files.
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

def load_afl_odds_data() -> Dict[str, Dict[str, float]]:
    """
    Load AFL 2GS and AGS odds from CSV files.
    Returns a dictionary with player name as key and a dict of their odds as value.
    """
    odds_data = {}
    
    # Load 2GS odds
    try:
        with open(AFL_2GS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                player_name = row['Player'].strip() if 'Player' in row else ""
                if not player_name:
                    continue
                
                gs_price = row['2GS_prices']
                if gs_price and gs_price != '':
                    if player_name not in odds_data:
                        odds_data[player_name] = {}
                    odds_data[player_name]['2GS'] = float(gs_price)
    except FileNotFoundError:
        print(f"Error: 2GS file '{AFL_2GS_CSV}' not found.")
    except Exception as e:
        print(f"Error loading 2GS data: {e}")
    
    # Load AGS odds
    try:
        with open(AFL_AGS_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                player_name = row['Player'].strip() if 'Player' in row else ""
                if not player_name:
                    continue
                
                ags_price = row['AGS_prices']
                if ags_price and ags_price != '':
                    if player_name not in odds_data:
                        odds_data[player_name] = {}
                    odds_data[player_name]['AGS'] = float(ags_price)
    except FileNotFoundError:
        print(f"Error: AGS file '{AFL_AGS_CSV}' not found.")
    except Exception as e:
        print(f"Error loading AGS data: {e}")
    
    return odds_data

def load_nrl_bets_from_csv() -> List[Dict[str, Any]]:
    """Load NRL upcoming bets from the CSV files."""
    try:
        matchups = load_nrl_matchup_data()
        odds_data = load_nrl_odds_data()
        
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
                            "team": player_info['team_name'],
                            "sport": "NRL"
                        })
                    
                    # Add 2+ bet if available
                    if '2+' in odds_data[player_name]:
                        game_bets.append({
                            "playerId": f"{player_name}_2+",
                            "playerName": player_name,
                            "market": "2+",
                            "odds": odds_data[player_name]['2+'],
                            "team": player_info['team_name'],
                            "sport": "NRL"
                        })
            
            # Only add games that have bets
            if game_bets:
                game_id = f"NRL2024_{matchup.replace(' vs ', '_')}"
                games_data.append({
                    "gameId": game_id,
                    "gameDescription": matchup,
                    "sport": "NRL",
                    "bets": game_bets
                })
        
        return games_data
        
    except Exception as e:
        print(f"Error loading NRL data from CSV: {e}")
        return []

def load_afl_bets_from_csv() -> List[Dict[str, Any]]:
    """Load AFL upcoming bets from the CSV files."""
    try:
        matchups = load_afl_matchup_data()
        odds_data = load_afl_odds_data()
        
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
                    # Add 2GS bet if available
                    if '2GS' in odds_data[player_name]:
                        game_bets.append({
                            "playerId": f"{player_name}_2GS",
                            "playerName": player_name,
                            "market": "2GS",
                            "odds": odds_data[player_name]['2GS'],
                            "team": player_info['team_name'],
                            "sport": "AFL"
                        })
                    
                    # Add AGS bet if available
                    if 'AGS' in odds_data[player_name]:
                        game_bets.append({
                            "playerId": f"{player_name}_AGS",
                            "playerName": player_name,
                            "market": "AGS",
                            "odds": odds_data[player_name]['AGS'],
                            "team": player_info['team_name'],
                            "sport": "AFL"
                        })
            
            # Only add games that have bets
            if game_bets:
                game_id = f"AFL2024_{matchup.replace(' vs ', '_')}"
                games_data.append({
                    "gameId": game_id,
                    "gameDescription": matchup,
                    "sport": "AFL",
                    "bets": game_bets
                })
        
        return games_data
        
    except Exception as e:
        print(f"Error loading AFL data from CSV: {e}")
        return []

def load_upcoming_bets(sport_type='nrl') -> List[Dict[str, Any]]:
    """
    Loads the available bets for the upcoming round based on sport type.
    
    Args:
        sport_type: One of 'nrl', 'afl', or 'combined'
        
    Returns:
        List of game data with available bets
    """
    all_games = []
    
    # Load NRL data if needed
    if sport_type in ['nrl', 'combined']:
        nrl_data = load_nrl_bets_from_csv()
        if nrl_data:
            all_games.extend(nrl_data)
        elif sport_type == 'nrl':
            # Only fall back to mock data if specifically requesting NRL data
            try:
                with open(MOCK_DATA_FILE, 'r') as f:
                    mock_data = json.load(f)
                # Add sport tag to mock data
                for game in mock_data:
                    game['sport'] = 'NRL'
                    for bet in game.get('bets', []):
                        bet['sport'] = 'NRL'
                all_games.extend(mock_data)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                print(f"Error loading mock data: {e}")
    
    # Load AFL data if needed
    if sport_type in ['afl', 'combined']:
        afl_data = load_afl_bets_from_csv()
        if afl_data:
            all_games.extend(afl_data)
    
    return all_games

def get_bets_grouped_by_game(sport_type='nrl') -> Dict[str, List[Dict[str, Any]]]:
    """Groups available bets by gameId for the selected sport(s)."""
    all_games_data = load_upcoming_bets(sport_type)
    grouped_bets = {}
    for game_data in all_games_data:
        game_id = game_data.get('gameId')
        bets = game_data.get('bets', [])
        game_desc = game_data.get('gameDescription', f'Game {game_id}')
        sport = game_data.get('sport', 'NRL')
        
        if game_id and bets:
            # Add game info to each bet for easier access later
            enriched_bets = []
            for bet in bets:
                # Ensure odds are floats
                try:
                    bet['odds'] = float(bet['odds'])
                    bet['gameId'] = game_id  # Add gameId to bet level
                    bet['gameDescription'] = game_desc  # Add gameDesc to bet level
                    bet['sport'] = sport  # Ensure sport is included
                    enriched_bets.append(bet)
                except (ValueError, TypeError):
                    print(f"Warning: Skipping bet with invalid odds: {bet}")
            if enriched_bets:
                grouped_bets[game_id] = enriched_bets
    return grouped_bets 