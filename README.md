# Conflux Community Member Tracker

A Streamlit dashboard for tracking member growth across Conflux Telegram groups and Discord. Features automated bi-weekly data collection, historical growth charts, and copy-paste ready summaries.

## Features

- **Automated Data Collection**: GitHub Actions runs every 2 weeks on Friday at 8pm Hong Kong Time
- **Web Scraping**: Extracts member counts from 14 Telegram groups and Discord
- **Historical Tracking**: SQLite database stores all historical data
- **Interactive Dashboard**:
  - Aggregated total member growth charts
  - Individual group growth tracking
  - Multiple time range views (bi-weekly, monthly, quarterly, 6-month, yearly)
  - Copy-paste ready summary with growth deltas
- **Manual Collection**: On-demand data collection via dashboard button

## Tracked Communities

### Telegram Groups (14)
- Conflux English
- Conflux Africa
- Conflux Arabic
- Conflux Chinese
- Conflux Web3 China
- Conflux French
- Conflux Indonesia
- Conflux Korea
- Conflux Persia
- Conflux Russian
- Conflux LATAM
- Conflux Turkish
- Conflux Ukraine
- Conflux Vietnam

### Discord
- Conflux Network Discord Server

## Setup

### Prerequisites
- Python 3.11+
- Chrome/Chromium (for Selenium web scraping)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <your-repo-url>
   cd "LST Count New"
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # OR
   venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will open at http://localhost:8501

### First Time Usage

1. Click **"Collect Data Now"** in the sidebar to gather initial data
2. The scraper will fetch member counts from all Telegram groups and Discord
3. Data is saved to `data/members.db`
4. Charts and summaries will appear once data is collected

## Automated Data Collection (GitHub Actions)

### Setup

1. **Push to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Enable GitHub Actions**:
   - Go to your repository Settings > Actions > General
   - Enable "Read and write permissions" for workflows
   - The workflow will run automatically every 2 weeks on Friday at 8pm HKT

3. **Manual Trigger**:
   - Go to Actions tab in GitHub
   - Select "Bi-weekly Data Collection"
   - Click "Run workflow"

### How It Works

- GitHub Actions workflow: [.github/workflows/collect_data.yml](.github/workflows/collect_data.yml)
- Collection script: [scripts/collect_data.py](scripts/collect_data.py)
- Runs `cron: '0 12 * * 5'` (every Friday at 12:00 UTC = 8pm HKT)
- Automatically commits updated database to repository

## Project Structure

```
.
├── app.py                      # Main Streamlit dashboard
├── requirements.txt            # Python dependencies
├── data/
│   └── members.db             # SQLite database (tracked in git)
├── src/
│   ├── data/
│   │   ├── scraper.py         # Web scraping logic
│   │   └── database.py        # Database operations
│   ├── components/            # Reusable UI components
│   └── utils/                 # Utility functions
├── scripts/
│   └── collect_data.py        # Automated collection script
└── .github/
    └── workflows/
        └── collect_data.yml   # GitHub Actions workflow
```

## Dashboard Features

### 1. Copy-Paste Summary
- Shows latest member counts with growth deltas
- Format: `Africa: 2812 (-49)`
- Easy to copy for reports

### 2. Total Aggregated Growth
- Line chart showing total members across all groups
- Time range filters: All Time, 2 Weeks, Month, Quarter, 6 Months, Year
- Growth metrics and percentages

### 3. Individual Group Charts
- Select specific groups to view
- Side-by-side comparison
- Individual growth metrics

### 4. Manual Data Collection
- Sidebar button to collect data on-demand
- Real-time scraping status
- Success/failure feedback

## Development

### Manual Data Collection
```bash
python scripts/collect_data.py
```

### Test Scraper
```bash
python src/data/scraper.py
```

### Test Database
```bash
python src/data/database.py
```

## Troubleshooting

### Web Scraping Issues

**Telegram scraping fails**:
- Telegram may have changed their HTML structure
- Update regex patterns in [src/data/scraper.py:60-90](src/data/scraper.py)
- Check the actual Telegram page source

**Discord scraping fails**:
- Discord heavily uses JavaScript rendering
- May require Discord bot API instead (more reliable)
- Set `use_selenium=True` in scraper for JS rendering

### GitHub Actions Issues

**Workflow not running**:
- Check Actions are enabled in repository settings
- Verify cron schedule syntax
- Check workflow run history in Actions tab

**Database not updating**:
- Ensure "Read and write permissions" are enabled
- Check workflow logs for errors
- Verify database file is tracked in git (not in .gitignore)

## Notes

- Database file (`data/members.db`) is tracked in git for automated updates
- Web scraping may be fragile if sites change structure
- Be respectful with scraping frequency (1 second delay between requests)
- Consider using official APIs when available

## License

MIT
