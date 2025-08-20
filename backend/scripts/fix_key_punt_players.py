"""
Quick fix for key punt FT% players
Updates only the most important players for punt FT% strategy
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import create_engine, text

# Key players for punt FT% builds
KEY_PUNT_TARGETS = {
    # MUST BE IN PUNT FT% (terrible FT shooters)
    'Giannis Antetokounmpo': (0.657, True),
    'Rudy Gobert': (0.638, True),
    'Clint Capela': (0.529, True),
    'Nic Claxton': (0.551, True),
    'Ben Simmons': (0.596, True),
    'Andre Drummond': (0.469, True),
    'Steven Adams': (0.544, True),
    'Mason Plumlee': (0.595, True),
    'Mitchell Robinson': (0.641, True),
    'Walker Kessler': (0.654, True),
    'Jusuf Nurkić': (0.694, True),
    'Jakob Poeltl': (0.626, True),
    
    # MUST NOT BE IN PUNT FT% (good FT shooters)
    'Karl-Anthony Towns': (0.836, False),
    'Nikola Jokić': (0.824, False),
    'Joel Embiid': (0.814, False),
    'Stephen Curry': (0.908, False),
    'Damian Lillard': (0.895, False),
    'Trae Young': (0.886, False),
    'Kevin Durant': (0.883, False),
    'Jayson Tatum': (0.833, False),
    'Bam Adebayo': (0.801, False),
    'Anthony Davis': (0.816, False),
    'Brook Lopez': (0.784, False),
    'Nikola Vučević': (0.791, False),
    'Myles Turner': (0.789, False),
    'Chet Holmgren': (0.793, False),
    
    # Borderline cases (70-75% FT)
    'Domantas Sabonis': (0.743, False),  # Decent FT for a big
    'Alperen Sengun': (0.694, True),     # Below 70%, punt fit
    'Evan Mobley': (0.678, True),        # Below 70%, punt fit
    'Jarrett Allen': (0.705, False),     # Just above 70%, borderline
}

def main():
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found")
        return
    
    print("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("Connected. Updating key players for punt FT% strategy...")
        print("-" * 60)
        
        updated = 0
        for player_name, (ft_pct, should_be_punt) in KEY_PUNT_TARGETS.items():
            # Check if player exists
            result = conn.execute(text("""
                SELECT p.id, f.projected_ft_pct, f.punt_ft_fit
                FROM players p
                JOIN fantasy_data f ON p.id = f.player_id
                WHERE p.name = :name
            """), {"name": player_name})
            
            row = result.first()
            if row:
                old_ft = row.projected_ft_pct
                old_punt = row.punt_ft_fit
                
                # Update if needed
                if abs(old_ft - ft_pct) > 0.01 or old_punt != should_be_punt:
                    conn.execute(text("""
                        UPDATE fantasy_data
                        SET projected_ft_pct = :ft_pct,
                            punt_ft_fit = :punt_fit
                        WHERE player_id = :player_id
                    """), {
                        'player_id': row.id,
                        'ft_pct': ft_pct,
                        'punt_fit': should_be_punt
                    })
                    
                    status = "PUNT TARGET" if should_be_punt else "NOT PUNT"
                    display_name = player_name.encode('ascii', 'replace').decode('ascii')
                    print(f"Updated: {display_name:25} FT: {ft_pct:.1%} -> {status}")
                    updated += 1
            else:
                display_name = player_name.encode('ascii', 'replace').decode('ascii')
                print(f"Not found: {display_name}")
        
        conn.commit()
        
        print("\n" + "=" * 60)
        print(f"Updated {updated} players")
        print("\nPunt FT% strategy should now recommend:")
        print("  TARGETS: Giannis, Gobert, Capela, Claxton, Drummond")
        print("  AVOID: KAT, Jokic, Embiid (all good FT shooters)")

if __name__ == "__main__":
    main()