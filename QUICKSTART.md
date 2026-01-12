# Quick Start Guide

Get the Conflux Community Member Tracker up and running in 5 minutes.

## Prerequisites

Before you start, make sure you have:
- **Python 3.11+** installed
- **Chrome browser** (for Selenium web scraping)
- **Terminal/Command prompt** access

On macOS, you may need to accept the Xcode license first:
```bash
sudo xcodebuild -license
```

## Step 0: Pre-flight Check (30 seconds)

Run this to verify your system is ready:
```bash
./preflight_check.sh
```

This checks for Python, Xcode license, internet, and Chrome. Fix any issues before proceeding.

## Step 1: Test Scraper (1 minute)

Test if web scraping works before full setup:
```bash
python3 test_scraper.py
```

This performs a quick test of Telegram and Discord scraping. If it works, proceed to setup.

## Step 2: Setup (2 minutes)

### Option A: Automated Setup (macOS/Linux)
```bash
./setup.sh
```

### Option B: Manual Setup (All platforms)
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# OR
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

## Step 3: Run the Dashboard (1 minute)

```bash
# Make sure venv is activated
source venv/bin/activate

# Start Streamlit
streamlit run app.py
```

Your browser will open to http://localhost:8501

## Step 4: Collect Initial Data (2 minutes)

1. In the dashboard sidebar, click **"🔄 Collect Data Now"**
2. Wait 15-30 seconds while it scrapes all groups
3. See the results in the sidebar
4. Charts and summaries will appear automatically

## What You'll See

### 1. Copy-Paste Summary
A text area with formatted member counts and growth deltas:
```
Africa: 2812 (-49)
Korea: 688 (-9)
Turkey: 2087 (+331)
...
```
Select all and copy for your reports!

### 2. Total Aggregated Growth Chart
Line chart showing total members across all groups over time.
Use the dropdown to filter by time range.

### 3. Individual Group Charts
Grid of charts showing each group's growth.
Select which groups to display using the multiselect.

## Setting Up Automated Collection

Want data collected automatically every 2 weeks?

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### 2. Enable GitHub Actions
1. Go to your repo on GitHub
2. Settings > Actions > General
3. Workflow permissions: **Enable "Read and write permissions"**
4. Save

### 3. Done!
The workflow will run automatically every Friday at 8pm Hong Kong Time.

You can also manually trigger it:
- Go to Actions tab
- Select "Bi-weekly Data Collection"
- Click "Run workflow"

## Troubleshooting

### "No data yet!"
- Click "Collect Data Now" in the sidebar
- Wait for the scraping to complete
- Check for any error messages

### Scraping Fails
- Some groups may fail if their pages are down
- Discord scraping is less reliable (may need bot API)
- Try running again - intermittent network issues are common

### Python Not Found
- Install Python 3.11+ from python.org
- On macOS: `brew install python3`
- On Windows: Download from python.org

### Virtual Environment Issues
- Make sure to activate: `source venv/bin/activate`
- You should see `(venv)` in your terminal prompt
- Deactivate with `deactivate` command

## Next Steps

- **Customize**: Edit group names in [src/data/scraper.py](src/data/scraper.py)
- **Schedule**: Adjust collection frequency in [.github/workflows/collect_data.yml](.github/workflows/collect_data.yml)
- **Extend**: Add more charts or metrics to [app.py](app.py)

See [README.md](README.md) for full documentation and [CLAUDE.md](CLAUDE.md) for development guidance.

## Need Help?

Check these files:
- [README.md](README.md) - Full documentation
- [CLAUDE.md](CLAUDE.md) - Technical architecture and development guide
- GitHub Issues - Report bugs or request features
