# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Conflux Community Member Tracker is a Streamlit-based analytics dashboard that tracks member growth across 14 Telegram groups and 1 Discord server. The application features automated bi-weekly data collection via GitHub Actions, historical growth visualization, and copy-paste ready summary reports.

**Key Features**:
- Automated web scraping of Telegram and Discord member counts
- SQLite database for historical tracking
- Interactive charts with multiple time ranges
- GitHub Actions for scheduled data collection every 2 weeks (Friday 8pm HKT)

## Development Commands

### First-Time Setup
```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Dashboard
```bash
# Activate venv first
source venv/bin/activate

# Run Streamlit app
streamlit run app.py
```
Opens at http://localhost:8501 with auto-reload on file changes.

### Testing Components

```bash
# Test web scraper
python src/data/scraper.py

# Test database operations
python src/data/database.py

# Run automated collection script
python scripts/collect_data.py
```

### Managing Dependencies
```bash
# Install new package
pip install package_name

# Update requirements.txt
pip freeze > requirements.txt
```

## Project Architecture

### Directory Structure

```
.
├── app.py                      # Main Streamlit dashboard application
├── requirements.txt            # Python dependencies
├── data/
│   └── members.db             # SQLite database (tracked in git for CI/CD)
├── src/
│   ├── data/
│   │   ├── scraper.py         # Web scraping (Telegram + Discord)
│   │   ├── database.py        # SQLite database operations
│   │   └── __init__.py
│   ├── components/            # Reusable Streamlit UI components
│   │   └── __init__.py
│   └── utils/                 # Utility functions
│       └── __init__.py
├── scripts/
│   └── collect_data.py        # Automated collection script for CI/CD
├── .github/
│   └── workflows/
│       └── collect_data.yml   # GitHub Actions workflow (bi-weekly)
├── .streamlit/
│   └── config.toml           # Streamlit theme and server config
└── pages/                    # Optional multi-page sections
```

### Core Components

#### 1. Data Collection ([src/data/scraper.py](src/data/scraper.py))

**MemberScraper class**:
- Scrapes member counts from Telegram public group pages
- Scrapes Discord server invite page
- Supports both requests (fast) and Selenium (JS rendering) modes
- Built-in rate limiting (1 second delay between requests)

**Tracked Groups**:
- 14 Telegram groups: English, Africa, Arabic, Chinese, Web3 China, French, Indonesia, Korea, Persia, Russian, LATAM, Turkish, Ukraine, Vietnam
- 1 Discord server

**Important**: Web scraping is fragile. If scraping fails:
- Check if site HTML structure changed
- Update regex patterns in `scrape_telegram_group()` method
- Consider using Selenium mode for JS-rendered content
- Discord may require bot API for reliable data

#### 2. Database Layer ([src/data/database.py](src/data/database.py))

**MemberDatabase class**:
- SQLite with SQLAlchemy ORM
- Single table: `member_counts` (id, timestamp, group_name, member_count)
- Indexed on timestamp and group_name for fast queries

**Key Methods**:
- `add_member_counts()`: Insert new collection batch
- `get_all_data()`: Returns pandas DataFrame of all data
- `get_latest_counts()`: Latest member count per group
- `get_previous_counts()`: Previous collection period (for deltas)
- `get_aggregated_totals()`: Sum of all groups over time
- `get_group_data()`: Historical data for specific group

**Database File**: `data/members.db` is tracked in git (not in .gitignore) to allow GitHub Actions to commit updates automatically.

#### 3. Dashboard ([app.py](app.py))

**Layout Structure**:
1. **Sidebar**: Manual data collection trigger, database stats, danger zone
2. **Copy-Paste Summary**: Text area with formatted growth deltas (e.g., "Africa: 2812 (-49)")
3. **Total Aggregated Growth**: Line chart with time range filters
4. **Individual Group Charts**: Grid of 2-column charts with metrics

**Streamlit Patterns Used**:
- `@st.cache_resource`: Caches database connection
- `@st.cache_data`: Caches expensive data queries (used in scraper)
- `st.session_state`: Would be used for persistent UI state (not currently needed)
- Wide layout with columns for responsive design

#### 4. Automation ([scripts/collect_data.py](scripts/collect_data.py) + [.github/workflows/collect_data.yml](.github/workflows/collect_data.yml))

**GitHub Actions Workflow**:
- Schedule: `cron: '0 12 * * 5'` = Every Friday at 12:00 UTC (8pm HKT)
- Uses Selenium mode for reliable JS rendering
- Commits database changes automatically
- Can be manually triggered via GitHub Actions UI

**Script Behavior**:
- Runs scraper in Selenium mode
- Saves successful scrapes to database
- Exits with error code if all scrapes fail
- Logs success/failure for each group

## Data Flow

### Manual Collection (via Dashboard)
```
User clicks "Collect Data Now"
  → MemberScraper.scrape_all()
    → Requests to each Telegram group URL
    → Parse HTML for member count
    → Requests to Discord invite page
  → MemberDatabase.add_member_counts()
    → Insert records with current timestamp
  → Dashboard refreshes with new data
```

### Automated Collection (GitHub Actions)
```
Cron trigger (every 2 weeks, Friday 8pm HKT)
  → GitHub Actions VM starts
  → Install Python + Chrome
  → Run scripts/collect_data.py
    → MemberScraper(use_selenium=True)
    → Scrape all groups
    → Save to database
  → Git commit + push database
  → Dashboard shows updated data on next view
```

### Visualization
```
Dashboard loads
  → MemberDatabase.get_all_data()
  → Filter by time range
  → Generate Plotly charts
    → Aggregated: sum by timestamp
    → Individual: filter by group_name
  → Calculate deltas from previous period
  → Render charts + summary
```

## Key Technical Details

### Web Scraping Strategy

**Telegram**:
- Public group pages at t.me/{group_name}
- Look for text patterns: "X members" or "X subscribers"
- Handles formatted numbers: "1,234" or "1.2K"
- May break if Telegram changes HTML structure

**Discord**:
- Invite page at discord.com/invite/{invite_code}
- JavaScript-rendered content (may need Selenium)
- Pattern: "X members" in page text
- Less reliable than Telegram scraping

**Rate Limiting**:
- 1 second delay between requests
- Respectful scraping to avoid IP bans

### Database Schema

```sql
CREATE TABLE member_counts (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    group_name VARCHAR(50) NOT NULL,
    member_count INTEGER NOT NULL
);

CREATE INDEX idx_group_timestamp ON member_counts(group_name, timestamp);
```

### Time Range Filtering

Time ranges in dashboard:
- **All Time**: No filter
- **Last 2 Weeks**: `timestamp >= now - 14 days`
- **Last Month**: `timestamp >= now - 30 days`
- **Last Quarter**: `timestamp >= now - 90 days`
- **Last 6 Months**: `timestamp >= now - 180 days`
- **Last Year**: `timestamp >= now - 365 days`

### Summary Format

Copy-paste summary format:
```
Africa: 2812 (-49)
Korea: 688 (-9)
Turkey: 2087 (+331)
```

Format: `{group_name}: {current_count} ({delta})`
- Delta calculated: current count - previous collection count
- Positive deltas: `(+X)`
- Negative deltas: `(-X)`
- Zero delta: `(0)`

## Development Workflow

### Adding a New Telegram Group

1. Add to `MemberScraper.TELEGRAM_GROUPS` dict in [src/data/scraper.py:22-37](src/data/scraper.py)
2. Key = display name, value = t.me URL
3. No code changes needed elsewhere (dynamic group loading)

### Modifying Scraping Logic

1. Test changes locally: `python src/data/scraper.py`
2. Update regex patterns in `scrape_telegram_group()` if HTML changed
3. Toggle `use_selenium=True` if JavaScript rendering needed
4. Be aware: GitHub Actions uses Selenium by default for reliability

### Adding Dashboard Features

1. Query data using `MemberDatabase` methods
2. Create Plotly figures with `px.line()`, `px.bar()`, etc.
3. Use `st.columns()` for side-by-side layout
4. Cache expensive operations with `@st.cache_data`
5. Test locally with `streamlit run app.py`

### Modifying GitHub Actions Schedule

1. Edit cron expression in [.github/workflows/collect_data.yml:6](.github/workflows/collect_data.yml)
2. Current: `'0 12 * * 5'` = Every Friday 12:00 UTC
3. Cron format: `minute hour day month weekday`
4. Convert HKT to UTC: HKT is UTC+8

Example schedules:
- Every Monday 9am HKT: `'0 1 * * 1'` (1am UTC)
- Every week Friday 8pm HKT: `'0 12 * * 5'` (current)
- Every 2 weeks: GitHub Actions doesn't support directly, use cron to run weekly and skip alternate weeks in script logic

## Troubleshooting

### Scraping Failures

**All Telegram scrapes fail**:
- Telegram may have changed HTML structure
- Open a Telegram group URL in browser, inspect HTML
- Update regex patterns in [src/data/scraper.py:60-90](src/data/scraper.py)
- Look for new div classes or text patterns

**Discord scraping fails**:
- Discord heavily uses JavaScript
- Try `MemberScraper(use_selenium=True)`
- Consider Discord bot API for reliable counts (requires bot token)

**Selenium errors in GitHub Actions**:
- Check Chrome installation in workflow YAML
- Verify `webdriver_manager` is in requirements.txt
- Check workflow logs for specific errors

### Database Issues

**Database file corrupted**:
- Backup current file
- Delete `data/members.db`
- Re-collect data manually
- Database will be recreated automatically

**Missing historical data**:
- Check git history: `git log data/members.db`
- Database may have been reset
- Cannot recover unless backed up

**Query performance slow**:
- Database has indexes on timestamp and group_name
- For large datasets (>10K rows), consider adding more indexes
- Current size should handle years of bi-weekly data easily

### GitHub Actions Issues

**Workflow not running automatically**:
- Check Settings > Actions > General > Workflow permissions
- Enable "Read and write permissions"
- Verify cron schedule is correct (use crontab.guru for validation)
- Check Actions tab for failed runs

**Database not updating after workflow**:
- Check workflow logs for scraping errors
- Verify git commit step succeeded
- Ensure database file is tracked (not in .gitignore)
- Check repository permissions

## Performance Considerations

### Dashboard Load Time
- SQLite queries are fast for current data size
- Bottleneck is Plotly chart rendering with many data points
- Consider data pagination if dataset grows to 100K+ rows

### Scraping Duration
- ~15-20 seconds for all 15 groups (with 1s delays)
- Selenium mode is slower: ~30-45 seconds
- GitHub Actions has 6-hour timeout (no issue for this use case)

### Database Size
- ~100 bytes per row
- Bi-weekly collection: 15 groups × 26 per year = 390 rows/year
- 10 years of data = ~4,000 rows = ~400 KB (negligible)

## Notes for AI Assistance

- Virtual environment MUST be activated before any Python commands
- Database file is intentionally tracked in git (not standard practice, but needed for CI/CD)
- Web scraping may break unexpectedly - always test before committing changes
- Selenium requires Chrome/Chromium installed (auto-managed by webdriver-manager)
- GitHub Actions runs on Ubuntu (Linux), test Selenium locally if possible
- Streamlit apps rerun entire script on interaction - use caching for expensive operations
- Time zones: HKT = UTC+8, cron schedules use UTC
- Copy-paste summary format is critical for user's reporting workflow - preserve exact format
- Bi-weekly schedule means ~26 data points per year per group
