from data_loader import load_upcoming_bets, get_bets_grouped_by_game
from logic import find_multi_combination
import math

def test_data_loading():
    """Test that data loading from CSV files works correctly."""
    games_data = load_upcoming_bets()
    print(f"Loaded {len(games_data)} games")
    
    if games_data:
        # Print the first game details
        first_game = games_data[0]
        print(f"\nFirst game: {first_game['gameDescription']}")
        print(f"Number of betting options: {len(first_game['bets'])}")
        
        # Print a few sample bets
        print("\nSample betting options:")
        for bet in first_game['bets'][:5]:  # Show first 5 bets
            print(f"  {bet['playerName']} - {bet['market']} @ {bet['odds']}")
    else:
        print("No games data loaded!")

def test_get_bets_grouped_by_game():
    """Test that bets are correctly grouped by game."""
    bets_by_game = get_bets_grouped_by_game()
    print(f"Grouped bets for {len(bets_by_game)} games")
    
    for game_id, bets in list(bets_by_game.items())[:3]:  # Show first 3 games
        print(f"\nGame: {game_id}")
        print(f"Number of betting options: {len(bets)}")
        
        # Count markets
        ats_count = sum(1 for bet in bets if bet['market'] == 'ATS')
        tpt_count = sum(1 for bet in bets if bet['market'] == '2+')
        print(f"ATS bets: {ats_count}, 2+ Tries bets: {tpt_count}")

def test_find_multi_combination():
    """Test that the algorithm can find valid multi-combinations."""
    bets_by_game = get_bets_grouped_by_game()
    
    # Test with a few different target odds
    test_stakes = [10, 20, 50]
    test_wins = [100, 200, 500]
    
    for stake in test_stakes:
        for win in test_wins:
            target_odds = win / stake
            print(f"\nSearching for multi with target odds: {target_odds:.2f} (${stake} -> ${win})")
            
            result_legs = find_multi_combination(bets_by_game, target_odds)
            
            if result_legs:
                print(f"Found multi with {len(result_legs)} legs:")
                actual_odds = math.prod(leg['odds'] for leg in result_legs)
                actual_win = actual_odds * stake
                print(f"Achieved odds: {actual_odds:.2f}, potential win: ${actual_win:.2f}")
                
                # Print the selected legs
                for leg in result_legs:
                    print(f"  {leg['playerName']} - {leg['market']} @ {leg['odds']} ({leg['gameDescription']})")
                
                # Verify that we have one bet per game
                game_ids = [leg['gameId'] for leg in result_legs]
                if len(game_ids) != len(set(game_ids)):
                    print("ERROR: Multiple bets from the same game!")
            else:
                print(f"No combination found for target odds {target_odds:.2f}")

if __name__ == "__main__":
    print("Testing data loading from CSV files...\n")
    test_data_loading()
    
    print("\n-----------------------------------\n")
    print("Testing bets grouped by game...\n")
    test_get_bets_grouped_by_game()
    
    print("\n-----------------------------------\n")
    print("Testing multi-combination finder...\n")
    test_find_multi_combination() 