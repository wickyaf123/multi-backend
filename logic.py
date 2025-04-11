import math
import time
import random
from typing import List, Dict, Any, Optional, Tuple, Set

# Tolerance for floating point comparisons
ODDS_TOLERANCE = 0.01  # e.g., target 10.0, accept 9.99 to 10.01

# Set minimum and maximum legs for a multi
MIN_LEGS = 2
MAX_LEGS = 8
MAX_COMBINED_LEGS = 17  # Higher limit for combined sports mode

# Maximum number of alternatives to return
MAX_ALTERNATIVES = 5

# Maximum time allowed for algorithm execution (in seconds)
MAX_EXECUTION_TIME = 10.0

# Maximum search space to consider
MAX_COMBINATIONS_ESTIMATE = 100000

# Maximum alternatives per player position
MAX_PLAYER_ALTERNATIVES = 3

def find_multi_combination(
    bets_by_game: Dict[str, List[Dict[str, Any]]],
    target_odds: float,
    num_alternatives: int = MAX_ALTERNATIVES,
    sport_type: str = 'nrl'
) -> Tuple[List[Dict[str, Any]], Dict[int, List[Dict[str, Any]]]]:
    """
    Finds a multi-bet combination that meets the target odds, plus alternative
    player suggestions for each position.
    
    Enforces constraints:
    - Only one player from each game
    - Minimum of MIN_LEGS (2) players
    - Maximum legs depends on sport type:
      - For 'nrl' or 'afl': MAX_LEGS (8) players
      - For 'combined': MAX_COMBINED_LEGS (17) players
    
    Returns:
    - Tuple containing:
        1. Best multi combination (list of bets)
        2. Dictionary mapping position index to list of alternative players
    """
    # Determine max legs based on sport type
    max_allowed_legs = MAX_COMBINED_LEGS if sport_type == 'combined' else MAX_LEGS
    
    # Randomize game order for variety in results
    game_ids = list(bets_by_game.keys())
    random.shuffle(game_ids)
    n_games = len(game_ids)
    
    # Estimate the search space size to abort early if it's too large
    total_bets = sum(len(bets) for bets in bets_by_game.values())
    avg_bets_per_game = total_bets / max(1, n_games)
    estimated_combinations = min(pow(avg_bets_per_game, max_allowed_legs), pow(2, n_games) * avg_bets_per_game)
    
    print(f"Estimated combinations: {estimated_combinations:.2e}, games: {n_games}, avg bets per game: {avg_bets_per_game:.2f}")
    print(f"Using max legs: {max_allowed_legs} for sport type: {sport_type}")
    
    if estimated_combinations > MAX_COMBINATIONS_ESTIMATE:
        print(f"WARNING: Search space too large ({estimated_combinations:.2e} > {MAX_COMBINATIONS_ESTIMATE})")
        print(f"Adjusting search strategy to handle large search space")
        # We'll proceed but with a shorter time limit and more aggressive pruning
    
    # Track multiple solutions with their differences from target odds
    all_solutions = []
    
    # Track start time to enforce maximum execution time
    start_time = time.time()
    time_limit_exceeded = False
    
    # For early termination if we find enough good solutions
    solutions_found = 0
    
    def backtrack(
        game_idx: int,
        current_product: float,
        current_selection: List[Dict[str, Any]]
    ) -> None:
        """Recursive helper function to find all valid combinations"""
        nonlocal time_limit_exceeded, solutions_found
        
        # Check if time limit exceeded
        if time.time() - start_time > MAX_EXECUTION_TIME:
            time_limit_exceeded = True
            return
            
        # Check if we already have enough solutions
        if solutions_found >= num_alternatives * 2:  # Get 2x to allow for filtering
            return
        
        # Check if we already have too many legs
        if len(current_selection) > max_allowed_legs:
            return

        # Check if current product is close enough to target and we have at least MIN_LEGS
        if len(current_selection) >= MIN_LEGS:
            if math.isclose(current_product, target_odds, rel_tol=0, abs_tol=ODDS_TOLERANCE):
                # Found a solution - make a deep copy and ensure it's valid
                solution = list(current_selection)
                if verify_one_bet_per_game(solution):
                    # Calculate the difference for sorting later
                    diff = abs(current_product - target_odds)
                    all_solutions.append((solution, diff, current_product))
                    solutions_found += 1
                return
        
        # If we're at the end of the games list, check if this is a valid solution
        if game_idx >= n_games:
            # If we have at least MIN_LEGS, track this as a potential solution
            if len(current_selection) >= MIN_LEGS:
                solution = list(current_selection)
                if verify_one_bet_per_game(solution):
                    diff = abs(current_product - target_odds)
                    # Only add if it's reasonably close to the target
                    if diff / target_odds <= 0.2:  # Within 20% of target
                        all_solutions.append((solution, diff, current_product))
                        solutions_found += 1
            return

        # More aggressive pruning for high target odds
        if target_odds > 50:
            # If we're not on track to reach the target, prune
            remaining_games = n_games - game_idx
            if current_product * pow(5.0, remaining_games) < target_odds * 0.5:
                # Even with all remaining games having high odds of 5.0, we can't get close
                return

        # Pruning conditions
        if current_product > target_odds * 1.1 and target_odds > 0:
            # If we've already overshot by 10%, prune
            return

        current_game_id = game_ids[game_idx]

        # Randomize: sometimes skip a game, sometimes include it
        # This adds variety to the results for the same inputs
        if random.random() < 0.5:
            # Option 1: Skip this game entirely
            backtrack(game_idx + 1, current_product, current_selection)
        
        # If time limit exceeded or we found enough, stop recursion
        if time_limit_exceeded or solutions_found >= num_alternatives * 2:
            return

        # Option 2: Try each bet from the current game
        # Shuffle bets within this game for more variety
        game_bets = list(bets_by_game[current_game_id])
        random.shuffle(game_bets)
        
        for bet in game_bets:
            odds = bet.get('odds', 1.0)
            if odds <= 0: continue  # Skip invalid odds

            current_selection.append(bet)
            backtrack(game_idx + 1, current_product * odds, current_selection)
            current_selection.pop()  # Backtrack: remove the bet
            
            # If time limit exceeded or we found enough, stop recursion
            if time_limit_exceeded or solutions_found >= num_alternatives * 2:
                return

    # Start the backtracking search
    # Start with product 1.0 and empty selection
    backtrack(0, 1.0, [])
    
    if time_limit_exceeded:
        print(f"WARNING: Time limit of {MAX_EXECUTION_TIME} seconds exceeded. Returning best solutions found so far.")
    
    # Sort solutions by how close they are to the target odds
    all_solutions.sort(key=lambda x: x[1])
    
    # Ensure we have valid solutions (one bet per game)
    valid_solutions = []
    
    # Process the solutions
    for solution, diff, final_odds in all_solutions[:num_alternatives * 2]:
        if not verify_one_bet_per_game(solution):
            solution = fix_multi_bets_same_game(solution)
        
        # Only keep solutions that have between MIN_LEGS and max_allowed_legs
        if MIN_LEGS <= len(solution) <= max_allowed_legs:
            # Double-check we're within tolerance
            actual_odds = math.prod(leg['odds'] for leg in solution)
            if abs(actual_odds - target_odds) / target_odds <= 0.1:  # Within 10% of target
                valid_solutions.append(solution)
    
    # If no valid solutions found, return empty results
    if not valid_solutions:
        return [], {}
    
    # Add randomization when selecting the best solution
    # Instead of always picking the first solution, randomly pick from the top 3 (if available)
    selection_count = min(3, len(valid_solutions))
    best_multi = random.choice(valid_solutions[:selection_count])
    
    # Now find alternative player suggestions for each position in the best multi
    alternatives_by_position = find_player_alternatives(best_multi, bets_by_game, target_odds)
    
    return best_multi, alternatives_by_position

def find_player_alternatives(
    main_multi: List[Dict[str, Any]],
    bets_by_game: Dict[str, List[Dict[str, Any]]],
    target_odds: float
) -> Dict[int, List[Dict[str, Any]]]:
    """
    Find alternative player suggestions for each position in the main multi.
    
    Args:
        main_multi: The main multi combination (list of bets)
        bets_by_game: All available bets grouped by game
        target_odds: The target odds to achieve
        
    Returns:
        Dictionary mapping position index to list of alternative players
    """
    alternatives_by_position = {}
    
    # Calculate the main multi's odds
    main_odds = math.prod(bet['odds'] for bet in main_multi)
    
    # For each position in the main multi
    for i, bet in enumerate(main_multi):
        position_alternatives = []
        game_id = bet['gameId']
        
        # Remove this bet's contribution to calculate what the replacement needs to achieve
        required_odds = target_odds / (main_odds / bet['odds'])
        
        # Find alternatives from the same game that give similar odds
        for alt_bet in bets_by_game[game_id]:
            # Skip the bet that's already in the multi
            if alt_bet['playerId'] == bet['playerId'] and alt_bet['market'] == bet['market']:
                continue
                
            # Check if this alternative would work
            odds_ratio = alt_bet['odds'] / required_odds
            
            # If the odds are within 20% of what we need, consider this alternative
            if 0.8 <= odds_ratio <= 1.2:
                # Calculate new expected multi odds with this alternative
                expected_odds = (main_odds / bet['odds']) * alt_bet['odds']
                
                # Add to alternatives with metadata about its impact on the overall multi
                alt_bet_with_meta = alt_bet.copy()
                alt_bet_with_meta['expectedMultiOdds'] = expected_odds
                alt_bet_with_meta['expectedDiff'] = abs(expected_odds - target_odds)
                position_alternatives.append(alt_bet_with_meta)
        
        # Sort alternatives by how close they get to the target odds
        position_alternatives.sort(key=lambda x: x['expectedDiff'])
        
        # Store the best alternatives for this position
        if position_alternatives:
            alternatives_by_position[i] = position_alternatives[:MAX_PLAYER_ALTERNATIVES]
    
    return alternatives_by_position

def verify_one_bet_per_game(bets: List[Dict[str, Any]]) -> bool:
    """Verify that there is only one bet per game in the multi."""
    game_ids = set()
    for bet in bets:
        game_id = bet.get('gameId')
        if game_id in game_ids:
            return False
        game_ids.add(game_id)
    return True

def fix_multi_bets_same_game(bets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fix a multi that has multiple bets from the same game.
    Keep the first one encountered for each game.
    """
    result = []
    game_ids = set()
    
    for bet in bets:
        game_id = bet.get('gameId')
        if game_id not in game_ids:
            result.append(bet)
            game_ids.add(game_id)
    
    return result 