"""
Load FT% data from JSON file to PostgreSQL database
This script reads the player_ft_data.json file and updates the database
"""

import sys
import os
import json
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def is_punt_ft_fit(ft_pct, position):
    """
    Determine if a player is a good punt FT% fit
    
    Rules:
    - Never mark players above 75% as punt fits
    - Centers/PFs below 70% are excellent punt fits
    - Any player below 65% is an excellent punt fit
    - Guards below 72% can work in punt builds
    """
    if ft_pct >= 0.750:
        return False  # Never punt with good FT shooters
    
    if ft_pct < 0.650:
        return True   # Always punt with terrible FT shooters
    
    if position in ['C', 'PF'] and ft_pct < 0.700:
        return True   # Centers/PFs below 70% are punt fits
    
    if ft_pct < 0.720:
        return True   # Anyone below 72% can work in punt builds
    
    return False

def load_ft_data_to_database():
    """Load FT% data from JSON file to database"""
    
    # Check if JSON file exists
    json_file = "player_ft_data.json"
    if not os.path.exists(json_file):
        print(f"Error: {json_file} not found!")
        print("Please run fetch_all_ft_data.py first to gather the data.")
        return
    
    # Load JSON data
    with open(json_file, 'r') as f:
        ft_data = json.load(f)
    
    print(f"Loaded data for {len(ft_data)} players from {json_file}")
    
    # Create database connection
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment")
        return
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        print("\n" + "=" * 70)
        print("UPDATING DATABASE WITH REAL FT% DATA")
        print("=" * 70)
        
        updates_made = 0
        skipped = 0
        punt_fits = []
        good_shooters = []
        biggest_changes = []
        
        for player_name, player_data in ft_data.items():
            db_player_id = player_data['db_player_id']
            position = player_data['position']
            adp_rank = player_data['adp_rank']
            current_db_ft = player_data['current_db_ft_pct']
            real_ft_pct = player_data.get('real_ft_pct')
            
            # Skip if we couldn't fetch real data
            if real_ft_pct is None:
                skipped += 1
                print(f"  Skipping {player_name} - no NBA API data available")
                continue
            
            # Determine punt fit based on real FT%
            is_punt_fit = is_punt_ft_fit(real_ft_pct, position)
            
            # Update database
            session.execute(text("""
                UPDATE fantasy_data
                SET projected_ft_pct = :ft_pct,
                    punt_ft_fit = :punt_fit
                WHERE player_id = :player_id
            """), {
                'player_id': db_player_id,
                'ft_pct': real_ft_pct,
                'punt_fit': is_punt_fit
            })
            
            updates_made += 1
            
            # Track for summary
            diff = abs(real_ft_pct - current_db_ft)
            if diff > 0.1:
                biggest_changes.append((player_name, current_db_ft, real_ft_pct, diff, adp_rank))
            
            if is_punt_fit and real_ft_pct < 0.70:
                punt_fits.append((player_name, position, real_ft_pct, adp_rank))
            elif real_ft_pct > 0.80:
                good_shooters.append((player_name, position, real_ft_pct, adp_rank))
            
            # Show progress for top players
            if adp_rank <= 30 or diff > 0.15:
                status = "PUNT FIT" if is_punt_fit else "GOOD FT%" if real_ft_pct > 0.75 else "NEUTRAL"
                display_name = player_name.encode('ascii', 'replace').decode('ascii')
                print(f"  ADP #{adp_rank:3} | {display_name:25} {position:3} | "
                      f"FT: {current_db_ft:.1%} -> {real_ft_pct:.1%} | {status}")
        
        # Commit changes
        session.commit()
        
        print("\n" + "=" * 70)
        print(f"DATABASE UPDATE COMPLETE")
        print("=" * 70)
        print(f"[SUCCESS] Updated: {updates_made} players")
        print(f"[SKIPPED] No data: {skipped} players")
        
        # Show punt FT% targets
        print("\n" + "=" * 70)
        print("TOP PUNT FT% TARGETS (Poor FT shooters < 70%):")
        print("-" * 70)
        
        punt_fits.sort(key=lambda x: x[2])  # Sort by FT%
        for name, pos, ft_pct, adp in punt_fits[:15]:
            display_name = name.encode('ascii', 'replace').decode('ascii')
            print(f"  ADP #{adp:3} - {display_name:25} ({pos}) - {ft_pct:.1%} FT")
        
        # Show players to avoid in punt builds
        print("\n" + "=" * 70)
        print("NEVER PUNT WITH THESE (Good FT shooters > 80%):")
        print("-" * 70)
        
        good_shooters.sort(key=lambda x: -x[2])  # Sort by FT% descending
        for name, pos, ft_pct, adp in good_shooters[:15]:
            display_name = name.encode('ascii', 'replace').decode('ascii')
            print(f"  ADP #{adp:3} - {display_name:25} ({pos}) - {ft_pct:.1%} FT")
        
        # Show biggest corrections
        print("\n" + "=" * 70)
        print("BIGGEST DATA CORRECTIONS:")
        print("-" * 70)
        
        biggest_changes.sort(key=lambda x: -x[3])  # Sort by difference
        for name, old_ft, new_ft, diff, adp in biggest_changes[:10]:
            display_name = name.encode('ascii', 'replace').decode('ascii')
            print(f"  ADP #{adp:3} - {display_name:25} | "
                  f"Was: {old_ft:.1%} -> Now: {new_ft:.1%} | Diff: {diff:.1%}")
        
        print("\n" + "=" * 70)
        print("PUNT FT% STRATEGY SUMMARY:")
        print("-" * 70)
        print("CORE TARGETS: Players with <65% FT (Giannis, Gobert, Capela, etc.)")
        print("GOOD TARGETS: Centers/PFs with 65-70% FT")
        print("BORDERLINE: Guards with 70-72% FT")
        print("NEVER TARGET: Anyone >75% FT (ruins the punt)")
        print("=" * 70)
        
    except Exception as e:
        print(f"Error updating database: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 70)
    print("FT% DATABASE LOADER")
    print("=" * 70)
    print("This script will:")
    print("1. Read player_ft_data.json file")
    print("2. Update projected_ft_pct with real NBA values")
    print("3. Recalculate punt_ft_fit flags based on thresholds")
    print("4. Show summary of changes")
    print("=" * 70)
    print()
    
    load_ft_data_to_database()