import math
from data_loader import get_bets_grouped_by_game
from logic import find_multi_combination, find_player_alternatives

def test_player_alternatives():
    """Test that the algorithm can find alternative players for each position in a multi."""
    bets_by_game = get_bets_grouped_by_game()
    
    # Test with a reasonable target odds
    stake = 10
    win_amount = 150
    target_odds = win_amount / stake
    
    print(f"\nSearching for multi with target odds: {target_odds:.2f} (${stake} -> ${win_amount})")
    
    # Find the main multi combination and player alternatives
    main_combination, alternatives_by_position = find_multi_combination(bets_by_game, target_odds)
    
    if main_combination:
        main_odds = math.prod(leg['odds'] for leg in main_combination)
        
        print(f"Found main multi with {len(main_combination)} legs:")
        print(f"Achieved odds: {main_odds:.2f}, potential win: ${main_odds * stake:.2f}")
        
        # Print the selected legs
        for i, leg in enumerate(main_combination):
            print(f"  Leg #{i+1}: {leg['playerName']} - {leg['market']} @ {leg['odds']} ({leg['gameDescription']})")
            
            # Print alternatives for this position if available
            alt_count = len(alternatives_by_position.get(i, []))
            if alt_count > 0:
                print(f"    Found {alt_count} alternatives for this position:")
                for j, alt in enumerate(alternatives_by_position[i]):
                    expected_multi_odds = alt['expectedMultiOdds']
                    print(f"      Alt #{j+1}: {alt['playerName']} - {alt['market']} @ {alt['odds']} " +
                          f"(new multi: {expected_multi_odds:.2f}, win: ${expected_multi_odds * stake:.2f})")
            else:
                print("    No alternatives found for this position")
    else:
        print(f"No combinations found for target odds {target_odds:.2f}")

def test_different_odds_alternatives():
    """Test finding player alternatives at different odds levels."""
    bets_by_game = get_bets_grouped_by_game()
    
    # Test with different target odds
    test_cases = [
        {"stake": 10, "win": 50},     # 5x odds
        {"stake": 10, "win": 200},    # 20x odds
        {"stake": 5, "win": 500},     # 100x odds
    ]
    
    for case in test_cases:
        stake = case["stake"]
        win = case["win"]
        target_odds = win / stake
        
        print(f"\n--- Testing with target odds: {target_odds:.2f} ---")
        main_combination, alternatives_by_position = find_multi_combination(bets_by_game, target_odds)
        
        if main_combination:
            main_odds = math.prod(leg['odds'] for leg in main_combination)
            print(f"Found main multi with {len(main_combination)} legs - odds: {main_odds:.2f}")
            
            # Count positions with alternatives
            positions_with_alts = len(alternatives_by_position)
            total_alternatives = sum(len(alts) for alts in alternatives_by_position.values())
            
            print(f"Found alternatives for {positions_with_alts} out of {len(main_combination)} positions")
            print(f"Total alternatives: {total_alternatives}, avg: {total_alternatives/max(1, positions_with_alts):.1f} per position")
            
            # Print a summary of each position
            for pos, alts in alternatives_by_position.items():
                main_leg = main_combination[pos]
                print(f"Position #{pos+1}: {main_leg['playerName']} ({main_leg['market']}) @ {main_leg['odds']}")
                print(f"  {len(alts)} alternatives - Odds range: {min(alt['odds'] for alt in alts):.2f} to {max(alt['odds'] for alt in alts):.2f}")
                # Calculate the odds deviation range of alternatives
                multi_odds_range = [alt['expectedMultiOdds'] for alt in alts]
                print(f"  Multi odds range: {min(multi_odds_range):.2f} to {max(multi_odds_range):.2f} (target: {target_odds:.2f})")
        else:
            print("No combinations found")

if __name__ == "__main__":
    print("Testing player alternatives for multi positions...\n")
    test_player_alternatives()
    
    print("\n-----------------------------------\n")
    print("Testing alternatives at different odds levels...\n")
    test_different_odds_alternatives() 