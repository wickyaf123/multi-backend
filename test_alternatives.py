import math
from data_loader import get_bets_grouped_by_game
from logic import find_multi_combination

def test_alternatives():
    """Test that the algorithm can find multiple alternative multi-combinations."""
    bets_by_game = get_bets_grouped_by_game()
    
    # Test with a reasonable target odds
    stake = 10
    win_amount = 150
    target_odds = win_amount / stake
    num_alternatives = 5
    
    print(f"\nSearching for up to {num_alternatives} multi combinations with target odds: {target_odds:.2f} (${stake} -> ${win_amount})")
    
    result_combinations = find_multi_combination(bets_by_game, target_odds, num_alternatives)
    
    if result_combinations:
        print(f"Found {len(result_combinations)} alternatives")
        
        for i, result_legs in enumerate(result_combinations):
            print(f"\nAlternative #{i+1} with {len(result_legs)} legs:")
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
                
            # Check uniqueness against previous alternatives
            if i > 0:
                previous_legs = result_combinations[i-1]
                # Count how many different legs they have
                differences = 0
                for leg in result_legs:
                    leg_key = (leg['gameId'], leg['playerId'], leg['market'])
                    if not any(prev_leg['gameId'] == leg['gameId'] and 
                               prev_leg['playerId'] == leg['playerId'] and 
                               prev_leg['market'] == leg['market'] for prev_leg in previous_legs):
                        differences += 1
                print(f"  This alternative differs from the previous one by {differences} legs")
    else:
        print(f"No combinations found for target odds {target_odds:.2f}")

def test_same_odds_different_combinations():
    """Test that the algorithm finds different combinations with similar odds."""
    bets_by_game = get_bets_grouped_by_game()
    
    # Multiple test cases with varying odds
    test_cases = [
        {"stake": 10, "win": 100},  # 10x odds
        {"stake": 10, "win": 200},  # 20x odds
        {"stake": 5, "win": 50},    # 10x odds
    ]
    
    for case in test_cases:
        stake = case["stake"]
        win = case["win"]
        target_odds = win / stake
        
        print(f"\n--- Testing with target odds: {target_odds:.2f} ---")
        result_combinations = find_multi_combination(bets_by_game, target_odds, 5)
        
        if result_combinations:
            print(f"Found {len(result_combinations)} alternatives")
            # Print summary of each combination
            for i, combo in enumerate(result_combinations):
                odds = math.prod(leg['odds'] for leg in combo)
                markets = [leg['market'] for leg in combo]
                market_counts = {
                    'ATS': markets.count('ATS'),
                    '2+': markets.count('2+')
                }
                print(f"Alternative #{i+1}: {len(combo)} legs, odds: {odds:.2f}, markets: {market_counts}")
        else:
            print("No combinations found")

if __name__ == "__main__":
    print("Testing multi-combination alternatives finder...\n")
    test_alternatives()
    
    print("\n-----------------------------------\n")
    print("Testing different combinations with similar odds...\n")
    test_same_odds_different_combinations() 