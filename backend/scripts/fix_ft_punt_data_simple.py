"""
Fix FT% data and punt_ft_fit flags using known NBA stats
Simple version that uses hardcoded data for key players
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Comprehensive FT% data for fantasy-relevant players
# Based on 2023-24 season or recent career averages
PLAYER_FT_DATA = {
    # Elite FT shooters (>85%) - NEVER punt FT% targets
    'Stephen Curry': 0.908,
    'Damian Lillard': 0.895,
    'Trae Young': 0.886,
    'Kyrie Irving': 0.878,
    'Kevin Durant': 0.883,
    'Karl-Anthony Towns': 0.836,
    'Jayson Tatum': 0.833,
    'Devin Booker': 0.878,
    'Shai Gilgeous-Alexander': 0.874,
    'Donovan Mitchell': 0.865,
    'Fred VanVleet': 0.870,
    'CJ McCollum': 0.850,
    'Paul George': 0.852,
    'Khris Middleton': 0.855,
    'Jalen Brunson': 0.829,
    
    # Good FT shooters (75-85%) - NOT punt FT% targets
    'Nikola Jokić': 0.824,
    'Joel Embiid': 0.814,
    'Bam Adebayo': 0.801,
    'Anthony Davis': 0.816,
    'LeBron James': 0.735,
    'Luka Dončić': 0.765,
    'Jaylen Brown': 0.765,
    'Anthony Edwards': 0.756,
    'Zach LaVine': 0.831,
    'DeMar DeRozan': 0.854,
    'Jimmy Butler': 0.858,
    'Kawhi Leonard': 0.883,
    'Pascal Siakam': 0.786,
    'Jaren Jackson Jr.': 0.803,
    'Kristaps Porzingis': 0.798,
    
    # Mediocre FT shooters (65-75%) - Borderline punt FT%
    'Domantas Sabonis': 0.743,
    'LaMelo Ball': 0.726,
    'Scottie Barnes': 0.734,
    'Cade Cunningham': 0.732,
    'Ja Morant': 0.748,
    'De\'Aaron Fox': 0.738,
    'Tyrese Haliburton': 0.780,  # Actually good, not punt
    'Dejounte Murray': 0.792,     # Actually good, not punt
    'Darius Garland': 0.834,      # Actually good, not punt
    'Alperen Sengun': 0.694,
    'Evan Mobley': 0.678,
    'Jarrett Allen': 0.705,
    'Ivica Zubac': 0.721,
    'Naz Reid': 0.737,
    'Daniel Gafford': 0.723,
    'Isaiah Stewart': 0.733,
    
    # Poor FT shooters (<65%) - IDEAL punt FT% targets
    'Giannis Antetokounmpo': 0.657,
    'Rudy Gobert': 0.638,
    'Clint Capela': 0.529,
    'Nic Claxton': 0.551,
    'Ben Simmons': 0.596,
    'Russell Westbrook': 0.656,
    'Zion Williamson': 0.700,  # Borderline
    'Jusuf Nurkić': 0.694,      # Borderline
    'Walker Kessler': 0.654,
    'Mitchell Robinson': 0.641,
    'Robert Williams III': 0.654,
    'Steven Adams': 0.544,
    'Andre Drummond': 0.469,
    'Mason Plumlee': 0.595,
    'Dwight Powell': 0.639,
    'Jakob Poeltl': 0.626,
    
    # Additional centers/bigs often in punt FT% builds
    'Brook Lopez': 0.784,        # Actually decent, not punt
    'Nikola Vučević': 0.791,     # Actually decent, not punt
    'Myles Turner': 0.789,        # Actually decent, not punt
    'Chet Holmgren': 0.793,      # Actually decent, not punt
    'Victor Wembanyama': 0.795,  # Actually decent, not punt
    'Paolo Banchero': 0.738,     # Borderline
    'Jonas Valančiūnas': 0.718,  # Borderline punt
    'Draymond Green': 0.713,     # Borderline punt
    'Josh Giddey': 0.736,        # Borderline
}

def is_punt_ft_fit(ft_pct, position):
    """
    Determine if a player is a good punt FT% fit
    
    Rules:
    - Centers/PFs below 70% are excellent punt fits
    - Any player below 65% is an excellent punt fit
    - Guards below 72% can work in punt builds
    - Never mark players above 75% as punt fits
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

def fix_ft_data():
    """Fix FT% data and punt_ft_fit flags in database"""
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment")
        return
    
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        # Get all players with fantasy data
        result = session.execute(text("""
            SELECT p.id, p.name, p.position, f.projected_ft_pct, f.punt_ft_fit, f.adp_rank
            FROM players p
            JOIN fantasy_data f ON p.id = f.player_id
            ORDER BY f.adp_rank
        """))
        
        all_players = list(result)
        updates_made = 0
        punt_fits = []
        not_punt_fits = []
        
        print("Updating FT% data for fantasy-relevant players...")
        print("=" * 70)
        
        for row in all_players:
            player_id = row.id
            player_name = row.name
            position = row.position
            old_ft_pct = row.projected_ft_pct
            old_punt_fit = row.punt_ft_fit
            adp = row.adp_rank
            
            # Get real FT% if we have it
            if player_name in PLAYER_FT_DATA:
                real_ft_pct = PLAYER_FT_DATA[player_name]
            else:
                # Keep existing FT% but fix punt_fit based on the value
                real_ft_pct = old_ft_pct
            
            # Determine correct punt fit
            new_punt_fit = is_punt_ft_fit(real_ft_pct, position)
            
            # Update if needed
            if abs(real_ft_pct - old_ft_pct) > 0.01 or new_punt_fit != old_punt_fit:
                session.execute(text("""
                    UPDATE fantasy_data
                    SET projected_ft_pct = :ft_pct,
                        punt_ft_fit = :punt_fit
                    WHERE player_id = :player_id
                """), {
                    'player_id': player_id,
                    'ft_pct': real_ft_pct,
                    'punt_fit': new_punt_fit
                })
                
                updates_made += 1
                
                # Track for summary
                if new_punt_fit:
                    punt_fits.append((player_name, position, real_ft_pct, adp))
                elif real_ft_pct > 0.75:
                    not_punt_fits.append((player_name, position, real_ft_pct, adp))
                
                # Show updates for key players
                if player_name in PLAYER_FT_DATA or adp <= 50:
                    status = "PUNT FIT" if new_punt_fit else "GOOD FT%" if real_ft_pct > 0.75 else "NEUTRAL"
                    display_name = player_name.encode('ascii', 'replace').decode('ascii')
                    print(f"ADP #{adp:3} | {display_name:25} {position:3} | FT: {real_ft_pct:.1%} | {status}")
        
        session.commit()
        
        print("\n" + "=" * 70)
        print(f"Updated {updates_made} players")
        
        # Show punt FT% build recommendations
        print("\n" + "=" * 70)
        print("IDEAL PUNT FT% TARGETS (Poor FT shooters):")
        print("-" * 70)
        
        # Sort by FT% to show worst shooters first
        punt_fits.sort(key=lambda x: x[2])
        
        print("\nELITE Punt Targets (<60% FT):")
        for name, pos, ft_pct, adp in punt_fits[:10]:
            if ft_pct < 0.60:
                display_name = name.encode('ascii', 'replace').decode('ascii')
                print(f"  ADP #{adp:3} - {display_name:25} ({pos}) - {ft_pct:.1%} FT")
        
        print("\nGOOD Punt Targets (60-70% FT):")
        count = 0
        for name, pos, ft_pct, adp in punt_fits:
            if 0.60 <= ft_pct < 0.70 and count < 10:
                display_name = name.encode('ascii', 'replace').decode('ascii')
                print(f"  ADP #{adp:3} - {display_name:25} ({pos}) - {ft_pct:.1%} FT")
                count += 1
        
        print("\n" + "=" * 70)
        print("AVOID IN PUNT FT% (Good FT shooters):")
        print("-" * 70)
        
        # Show best FT shooters that should never be in punt builds
        not_punt_fits.sort(key=lambda x: -x[2])
        for name, pos, ft_pct, adp in not_punt_fits[:10]:
            display_name = name.encode('ascii', 'replace').decode('ascii')
            print(f"  ADP #{adp:3} - {display_name:25} ({pos}) - {ft_pct:.1%} FT")
        
        print("\n" + "=" * 70)
        print("PUNT FT% BUILD STRATEGY:")
        print("-" * 70)
        print("TARGET: Players <70% FT (Centers/PFs) or <65% FT (any position)")
        print("AVOID: Players >75% FT (ruins the punt strategy)")
        print("CORE: Giannis, Gobert, Capela, Claxton, Simmons")
        print("COMPLEMENT: High FG%, REB, BLK to maximize punt effectiveness")
        
    except Exception as e:
        print(f"Error: {e}")
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    print("FT% Data Fix Script (Simple Version)")
    print("=" * 70)
    print("Using hardcoded FT% data for key fantasy players")
    print("=" * 70)
    print()
    
    fix_ft_data()