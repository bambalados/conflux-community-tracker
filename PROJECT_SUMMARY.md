# Project Summary: Conflux Community Member Tracker

## What Was Built

A complete Streamlit-based analytics dashboard that tracks member growth across 14 Telegram groups and 1 Discord server for the Conflux Network community.

## Key Features Implemented

### ✅ 1. Automated Data Collection
- **Web scraping** of Telegram and Discord member counts
- **GitHub Actions workflow** that runs every 2 weeks (Friday 8pm HKT)
- **Manual collection** via dashboard button for on-demand updates
- Supports both requests (fast) and Selenium (reliable) scraping modes

### ✅ 2. Historical Data Storage
- **SQLite database** for persistent storage
- Tracks timestamp, group name, and member count
- Database file tracked in git for automated CI/CD updates
- Indexed for fast queries

### ✅ 3. Interactive Dashboard

#### a) Copy-Paste Summary Bar
- Formatted text showing current counts and growth deltas
- Example format: `Africa: 2812 (-49)`
- Easy to select and copy for reports
- Shows change from previous bi-weekly collection

#### b) Aggregated Total Growth Chart
- Line chart showing sum of all members over time
- Time range filters: All Time, 2 Weeks, Month, Quarter, 6 Months, Year
- Growth metrics and percentages
- Interactive Plotly visualization

#### c) Individual Group Charts
- Grid layout showing each group's growth
- Multi-select to choose which groups to display
- Same time range filters as aggregated chart
- Growth metrics per group

### ✅ 4. Automation & CI/CD
- GitHub Actions workflow for scheduled collection
- Automatic database commits after each collection
- Manual trigger option via GitHub UI
- Chrome/Selenium setup for JavaScript-rendered pages

## File Structure

```
LST Count New/
├── app.py                          # Main Streamlit dashboard
├── requirements.txt                # Python dependencies
├── setup.sh                        # Automated setup script
├── README.md                       # Full documentation
├── QUICKSTART.md                   # 5-minute quick start
├── CLAUDE.md                       # AI assistant guidance (detailed)
├── data/
│   └── members.db                  # SQLite database (created on first run)
├── src/
│   ├── data/
│   │   ├── scraper.py             # Web scraping logic
│   │   └── database.py            # Database operations
│   ├── components/                # Reusable UI components (empty, ready for use)
│   └── utils/                     # Utility functions (empty, ready for use)
├── scripts/
│   └── collect_data.py            # Automated collection for CI/CD
├── .github/
│   └── workflows/
│       └── collect_data.yml       # GitHub Actions workflow
└── .streamlit/
    └── config.toml                # Streamlit theme config
```

## Technologies Used

- **Streamlit**: Web dashboard framework
- **Pandas**: Data manipulation
- **Plotly**: Interactive charts
- **SQLAlchemy**: Database ORM
- **SQLite**: Database storage
- **BeautifulSoup**: HTML parsing
- **Selenium**: JavaScript rendering for web scraping
- **Requests**: HTTP requests
- **GitHub Actions**: Automated scheduling

## Tracked Communities (15 total)

### Telegram (14 groups)
1. Conflux English
2. Conflux Africa
3. Conflux Arabic
4. Conflux Chinese
5. Conflux Web3 China
6. Conflux French
7. Conflux Indonesia
8. Conflux Korea
9. Conflux Persia
10. Conflux Russian
11. Conflux LATAM
12. Conflux Turkish
13. Conflux Ukraine
14. Conflux Vietnam

### Discord (1 server)
15. Conflux Network Discord

## How It Works

### Data Collection Flow
1. **Scraper** visits each Telegram group's public page
2. Extracts member count using regex patterns
3. Visits Discord invite page for member count
4. **Database** stores timestamp, group name, and count
5. **Dashboard** queries database and generates visualizations

### Automated Schedule
- **Frequency**: Every 2 weeks
- **Day**: Friday
- **Time**: 8pm Hong Kong Time (12:00 UTC)
- **Mechanism**: GitHub Actions cron job
- **Result**: Database automatically updated in repository

### Manual Collection
- Click button in dashboard sidebar
- Scrapes all 15 groups in ~15-30 seconds
- Saves to local database
- Charts update immediately

## Getting Started

### Quick Start (5 minutes)
```bash
# 1. Setup
./setup.sh

# 2. Run dashboard
source venv/bin/activate
streamlit run app.py

# 3. Collect data via dashboard button
```

See [QUICKSTART.md](QUICKSTART.md) for detailed steps.

### Enable Automation
```bash
# Push to GitHub
git init
git add .
git commit -m "Initial commit"
git push -u origin main

# Enable GitHub Actions in repo settings
# Settings > Actions > Enable "Read and write permissions"
```

## Important Notes

### For Users
- First time: Click "Collect Data Now" to get initial data
- Copy-paste summary format is optimized for reports
- Web scraping may occasionally fail (network issues, site changes)
- Database grows slowly: ~390 rows/year at bi-weekly collection

### For Developers
- Virtual environment must be activated for all Python commands
- Database file is tracked in git (unusual but needed for CI/CD)
- Web scraping is fragile - may break if sites change HTML
- Selenium requires Chrome/Chromium installed
- GitHub Actions runs on Ubuntu Linux

### Customization
- Add/remove groups: Edit `TELEGRAM_GROUPS` in [src/data/scraper.py:22](src/data/scraper.py)
- Change schedule: Edit cron in [.github/workflows/collect_data.yml:6](.github/workflows/collect_data.yml)
- Modify charts: Edit Plotly code in [app.py](app.py)

## Documentation Files

- **README.md**: Complete user and developer documentation
- **QUICKSTART.md**: 5-minute getting started guide
- **CLAUDE.md**: Comprehensive technical architecture guide for AI assistants
  - Project architecture and data flow
  - Development workflows
  - Troubleshooting guides
  - Performance considerations
- **PROJECT_SUMMARY.md**: This file - high-level overview

## Next Steps

1. **Test locally**: Run setup and collect initial data
2. **Push to GitHub**: Enable automated collection
3. **Monitor**: Check GitHub Actions runs every 2 weeks
4. **Use**: Copy summary data for reports, analyze growth trends

## Potential Enhancements

Future improvements could include:
- Discord bot API for more reliable Discord data
- Email notifications when data is collected
- Export charts as images
- Historical comparison features
- Growth rate predictions
- Alert system for significant changes

---

**Project Status**: ✅ Complete and ready to use

**Prerequisites**: Python 3.11+, Chrome browser, GitHub account (for automation)

**Time to First Data**: ~5 minutes after setup
