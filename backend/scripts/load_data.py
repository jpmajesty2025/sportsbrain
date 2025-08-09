"""
Management script for loading SportsBrain data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import argparse
import logging
from app.data_loaders.player_loader import load_all_player_data

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main():
    parser = argparse.ArgumentParser(description='Load SportsBrain data')
    parser.add_argument('--players', action='store_true', help='Load player data')
    parser.add_argument('--limit', type=int, help='Limit number of records (for testing)')
    parser.add_argument('--test', action='store_true', help='Test mode - load only 10 players')
    
    args = parser.parse_args()
    
    if args.test:
        args.limit = 10
        
    if args.players:
        print(f"Loading player data{' (limited to ' + str(args.limit) + ')' if args.limit else ''}...")
        load_all_player_data(limit=args.limit)
        print("Player data loaded successfully!")
    else:
        print("Please specify what to load: --players")


if __name__ == "__main__":
    main()