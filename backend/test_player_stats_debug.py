"""Debug player stats function"""
from app.db.database import get_db
from sqlalchemy import text

def test_analyze_player_stats():
    """Test the SQL query directly"""
    try:
        db = next(get_db())
        
        player_name = "Scoot Henderson"
        
        # Run the exact query from analyze_player_stats_enhanced
        result = db.execute(text("""
            SELECT 
                p.name, p.position, p.team,
                EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date)) as age,
                f.adp_rank, f.adp_round,
                f.projected_ppg, f.projected_rpg, f.projected_apg,
                f.projected_spg, f.projected_bpg,
                f.projected_fg_pct, f.projected_ft_pct, f.projected_3pm,
                f.projected_fantasy_ppg,
                f.consistency_rating, f.injury_risk,
                f.breakout_candidate, f.sleeper_score,
                gs.ppg as last_season_ppg,
                gs.rpg as last_season_rpg,
                gs.apg as last_season_apg
            FROM players p
            JOIN fantasy_data f ON p.id = f.player_id
            LEFT JOIN (
                SELECT player_id,
                       AVG(points) as ppg,
                       AVG(rebounds) as rpg,
                       AVG(assists) as apg
                FROM game_stats
                GROUP BY player_id
            ) gs ON p.id = gs.player_id
            WHERE LOWER(p.name) LIKE LOWER(:name)
            LIMIT 1
        """), {"name": f"%{player_name}%"})
        
        player = result.first()
        if player:
            print(f"Found player: {player.name}")
            print(f"Age type: {type(player.age)}, value: {player.age}")
            print(f"last_season_ppg type: {type(player.last_season_ppg)}, value: {player.last_season_ppg}")
            print(f"projected_ppg type: {type(player.projected_ppg)}, value: {player.projected_ppg}")
            
            # Test the comparison that's failing
            if player.age:
                print(f"\nTesting age comparison...")
                try:
                    if player.age < 25:
                        print("Age < 25: SUCCESS")
                except Exception as e:
                    print(f"Age < 25: ERROR - {e}")
            
            # Test ppg comparison
            if player.last_season_ppg:
                print(f"\nTesting ppg comparison...")
                try:
                    if player.last_season_ppg > 0:
                        print("last_season_ppg > 0: SUCCESS")
                except Exception as e:
                    print(f"last_season_ppg > 0: ERROR - {e}")
        else:
            print(f"Player {player_name} not found")
            
    except Exception as e:
        print(f"Query error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_analyze_player_stats()