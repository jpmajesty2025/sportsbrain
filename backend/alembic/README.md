# Alembic Migrations

## Migration History

1. **001_phase1a_model_enhancements.py** - Initial Phase 1A model enhancements
2. **002_add_phase1a_columns.py.skip** - Skipped (duplicate changes)
3. **003_add_missing_phase1a_columns.py** - Add missing Phase 1A columns with existence checks
4. **004_add_fantasy_data_table.py** - Add FantasyData table for draft preparation
5. **005_add_user_preferences_table.py** - Add UserPreferences table for theme and settings

## Running Migrations

```bash
# Check current version
alembic current

# Run all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

## Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration
alembic revision -m "Description of changes"
```

## Important Notes

- Always ensure `down_revision` points to the previous migration
- Use consistent naming: `XXX_description.py` where XXX is the sequence number
- Test migrations both up and down before deploying