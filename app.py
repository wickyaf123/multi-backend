from flask import Flask, request, jsonify
from flask_cors import CORS
import math
import traceback
import time
import os

from data_loader import get_bets_grouped_by_game
from logic import find_multi_combination, ODDS_TOLERANCE, MAX_ALTERNATIVES, MAX_PLAYER_ALTERNATIVES

app = Flask(__name__)
# Get allowed origins from environment variable or use default
allowed_origins = os.environ.get('ALLOWED_ORIGINS', 'http://localhost:3000,https://multi-frontend-mu.vercel.app').split(',')
# Enable CORS for all routes, not just /api/* to be safe
CORS(app, origins=allowed_origins, supports_credentials=True)

@app.route('/api/generate-multi', methods=['POST'])
def generate_multi():
    # Log the request to help with debugging
    print(f"Received request from: {request.origin if hasattr(request, 'origin') else 'Unknown'}")
    print(f"Request method: {request.method}")
    print(f"Request headers: {request.headers}")
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    try:
        stake = float(data.get('stake', 0))
        win_amount = float(data.get('winAmount', 0))
        # New parameter to control number of alternatives (optional)
        num_alternatives = int(data.get('alternatives', MAX_PLAYER_ALTERNATIVES))
        # Get sport type (nrl, afl, or combined)
        sport_type = data.get('sportType', 'nrl')
        
        # Validate sport type
        if sport_type not in ['nrl', 'afl', 'combined']:
            sport_type = 'nrl'  # Default to NRL if invalid
            
        print(f"Sport type selected: {sport_type}")

        if stake <= 0 or win_amount <= stake:  # Win must be greater than stake
            return jsonify({"error": "Stake must be positive, and desired win must be greater than stake."}), 400

        target_odds = win_amount / stake
        
        # Sanity check on requested odds
        if target_odds > 1000:
            return jsonify({
                "error": f"Target odds of {target_odds:.2f} are too high. Please reduce your desired win amount or increase your stake."
            }), 400

    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid stake or win amount. Must be numbers. Details: {str(e)}"}), 400

    # --- Core Logic ---
    try:
        print(f"Processing request: stake=${stake}, win=${win_amount}, target_odds={target_odds:.2f}, sport={sport_type}")
        start_time = time.time()
        
        # Get fresh data each time based on sport type
        bets_by_game = get_bets_grouped_by_game(sport_type)
        if not bets_by_game:
            return jsonify({"error": f"Could not load betting data for {sport_type}."}), 500
            
        print(f"Loaded betting data with {len(bets_by_game)} games for {sport_type}")

        # Find the best multi combination and player alternatives - pass sport_type parameter
        main_combination, alternatives_by_position = find_multi_combination(
            bets_by_game, 
            target_odds, 
            num_alternatives,
            sport_type
        )
        
        elapsed_time = time.time() - start_time
        print(f"Search completed in {elapsed_time:.2f} seconds")
        
        if main_combination:
            # Calculate the actual odds achieved by the found legs
            actual_odds = math.prod(leg['odds'] for leg in main_combination)
            actual_win = actual_odds * stake
            
            # Format the response with player alternatives for each position
            player_alternatives = {}
            for position_idx, alt_bets in alternatives_by_position.items():
                # Create a more manageable format for the frontend
                formatted_alts = []
                for alt_bet in alt_bets:
                    # Exclude some internal metadata from the response
                    alt_copy = {k: v for k, v in alt_bet.items() if k not in ['expectedDiff']}
                    # Add the potential new multi odds and win
                    alt_copy['newMultiOdds'] = round(alt_copy.pop('expectedMultiOdds', 0), 2)
                    alt_copy['newPotentialWin'] = round(alt_copy['newMultiOdds'] * stake, 2)
                    formatted_alts.append(alt_copy)
                
                # Store by position index (as string for JSON)
                player_alternatives[str(position_idx)] = formatted_alts
            
            return jsonify({
                "message": "Multi combination found with player alternatives.",
                "targetOdds": target_odds,
                "stake": stake,
                "sportType": sport_type,
                "combination": {
                    "legs": main_combination,
                    "achievedOdds": round(actual_odds, 2),
                    "potentialWin": round(actual_win, 2)
                },
                "playerAlternatives": player_alternatives
            }), 200
        else:
            print(f"No combinations found for target odds {target_odds:.2f} with {sport_type}")
            return jsonify({
                "message": f"No combination found matching target odds of {target_odds:.2f} (within tolerance {ODDS_TOLERANCE}) for {sport_type}. Try different stake/win amounts or sport selection.",
                "targetOdds": target_odds,
                "sportType": sport_type,
                "combination": None,
                "playerAlternatives": {}
            }), 404  # Not Found might be appropriate

    except Exception as e:
        # Enhanced error logging
        error_traceback = traceback.format_exc()
        print(f"Error during multi generation: {e}")
        print(f"Traceback: {error_traceback}")
        return jsonify({
            "error": "An internal server error occurred while generating multis.",
            "details": str(e)
        }), 500

# Health check endpoint for Railway
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Multi-Backend is running (NRL + AFL)"}), 200

if __name__ == '__main__':
    # Get port from environment variable or use default
    port = int(os.environ.get('PORT', 5001))
    app.run(debug=False, host='0.0.0.0', port=port) 