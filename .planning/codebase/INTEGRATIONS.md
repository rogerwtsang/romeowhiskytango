# External Integrations

**Analysis Date:** 2026-01-10

## APIs & External Services

**Baseball Data (Primary):**
- pybaseball / Baseball Reference / FanGraphs
  - SDK/Client: `pybaseball` npm package v2.2.7+
  - Auth: None required (public API)
  - Integration: `src/data/scraper.py`
  - Functions used:
    - `get_team_batting_stats()` - Team roster stats by season
    - `get_player_batting_stats()` - Individual player stats
    - `get_league_batting_stats()` - League-wide aggregates
  - Data available: BA, OBP, SLG, ISO, H, 2B, 3B, HR, SB, CS, K%
  - Caching enabled: `pyb.cache.enable()` (line 16)

**MLB Stats API (Optional):**
- statsapi package (conditionally imported)
  - Integration: `src/data/scraper.py` (lines 260-299)
  - Function: `get_team_roster_positions()`
  - Purpose: Fielding position data
  - Status: Try/except import - gracefully degrades if not installed

**Payment Processing:**
- Not applicable

**Email/SMS:**
- Not applicable

## Data Storage

**Databases:**
- None (no SQL, MongoDB, etc.)

**File Storage:**
- Local filesystem only
  - Location: `data/` directory
  - Subdirectories: `raw/`, `processed/`, `analysis/`, `validation/`
  - Format: CSV files
  - Functions: `save_data()`, `load_data()` in `src/data/scraper.py`

**Caching:**
- pybaseball built-in caching (API response caching)
- In-memory results storage (`src/gui/utils/results_manager.py`)
  - Stores up to 10 simulation results for comparison

## Authentication & Identity

**Auth Provider:**
- Not applicable (desktop application, no user auth)

**OAuth Integrations:**
- Not applicable

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry, etc.)

**Analytics:**
- None detected

**Logs:**
- Console output only (`print()` statements)
- No structured logging framework

## CI/CD & Deployment

**Hosting:**
- Desktop application (not deployed)

**CI Pipeline:**
- Not detected (no `.github/workflows/`)

## Environment Configuration

**Development:**
- Required: Python 3.13+, packages from `requirements.txt`
- Secrets: None required
- Data: Local CSV files in `data/` directory

**Staging:**
- Not applicable

**Production:**
- Desktop application
- No secrets management needed
- Local filesystem storage

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Data Processing Pipeline

```
pybaseball API → CSV files → Player objects → Simulation → Results
      ↓              ↓              ↓             ↓           ↓
   scraper.py   data/raw/    processor.py   batch.py   ResultsManager
```

## External Services Summary

| Service | Type | Status | Integration Point |
|---------|------|--------|-------------------|
| Baseball Reference/FanGraphs | Data API | Active | `src/data/scraper.py` |
| MLB Stats API | Data API | Optional | `src/data/scraper.py` (statsapi) |
| Local Filesystem | Storage | Active | `data/` directory |

## Not Detected

- Databases (SQL, MongoDB, etc.)
- Cloud platforms (AWS, GCP, Azure)
- Payment processors
- Analytics services
- Authentication providers
- Message queues
- Webhooks or serverless functions
- Web frameworks (Flask, Django, FastAPI)

---

*Integration audit: 2026-01-10*
*Update when adding/removing external services*
