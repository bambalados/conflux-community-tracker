# Testing Guide

This guide helps you test the application in a safe environment before full deployment.

## Testing Strategy

We'll test in stages:
1. **System Check**: Verify prerequisites
2. **Scraper Test**: Test web scraping without database
3. **Local Dashboard**: Test full app locally
4. **Data Validation**: Verify collected data is correct

---

## Stage 1: System Check (30 seconds)

Verify your system meets all requirements:

```bash
./preflight_check.sh
```

**What it checks:**
- ✅ Xcode Command Line Tools installed
- ✅ Xcode license accepted
- ✅ Python 3.11+ available
- ✅ Internet connectivity
- ✅ Chrome browser (for Selenium)

**Fix any issues** before proceeding to the next stage.

### Common Issues

**Xcode license not accepted:**
```bash
sudo xcodebuild -license
```

**Python too old:**
```bash
brew install python@3.11
```

**No Chrome:**
```bash
brew install --cask google-chrome
```

---

## Stage 2: Scraper Test (1-2 minutes)

Test web scraping without setting up the full environment:

```bash
python3 test_scraper.py
```

**What it tests:**
- 🌐 Network connectivity to Telegram
- 🌐 Network connectivity to Discord
- 📄 Can fetch and parse HTML
- 🔍 Can extract member counts

### Expected Results

**Success:**
```
✅ Successfully fetched https://t.me/Conflux_English
✅ Found member count: 5,234
✅ Successfully fetched Discord invite page
```

**Partial Success:**
```
✅ Successfully fetched pages
⚠️  Could not find member count
```
This is okay! Telegram pages vary by region. The full scraper handles this.

**Failure:**
```
❌ Network error: Connection timeout
```
Check your internet connection or firewall settings.

---

## Stage 3: Full Setup & Local Test (5 minutes)

Now set up the full environment and test the dashboard:

### 3.1 Setup
```bash
./setup.sh
```

This creates a virtual environment and installs all dependencies.

### 3.2 Activate Environment
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### 3.3 Run Dashboard
```bash
streamlit run app.py
```

Browser opens to http://localhost:8501

### 3.4 Test Manual Collection

1. In the sidebar, click **"🔄 Collect Data Now"**
2. Wait 15-30 seconds
3. Check the results in the sidebar

**Expected behavior:**
- Shows "Scraping member counts..." spinner
- Displays success count: "✅ Collected data for X groups"
- Lists each group with member count
- May show warnings for failed groups (this is normal)

### 3.5 Verify Dashboard

After collection, check:

- ✅ **Copy-Paste Summary** appears with formatted text
- ✅ **Total Aggregated Growth** chart shows data
- ✅ **Individual Group Charts** display (select groups if needed)
- ✅ Sidebar shows database stats (collection points, last update)

---

## Stage 4: Data Validation (2 minutes)

Verify the collected data is accurate:

### 4.1 Manual Verification

1. Open a few Telegram groups in your browser:
   - https://t.me/Conflux_English
   - https://t.me/ConfluxAfrica
   - https://t.me/ConfluxKorea

2. Compare member counts shown on Telegram with dashboard data

3. Check Discord: https://discord.com/invite/confluxnetwork

### 4.2 Check Database

```bash
# Activate venv first
source venv/bin/activate

# Check database contents
python3 -c "
from src.data.database import MemberDatabase
db = MemberDatabase()
data = db.get_all_data()
print(f'Total records: {len(data)}')
print(f'Groups tracked: {len(data[\"group_name\"].unique())}')
print(f'Collection timestamps: {data[\"timestamp\"].nunique()}')
print('\nLatest counts:')
print(db.get_latest_counts())
db.close()
"
```

**Expected output:**
```
Total records: 15
Groups tracked: 15
Collection timestamps: 1
Latest counts:
{'English': (5234, datetime(...)), 'Africa': (2812, datetime(...)), ...}
```

### 4.3 Test Time Range Filters

In the dashboard:
1. Change "Select Time Range" dropdown
2. Verify chart updates correctly
3. Try different time ranges (All Time, 2 Weeks, Month, etc.)

### 4.4 Test Copy-Paste Feature

1. Select all text in the copy-paste summary box
2. Copy to clipboard
3. Paste in a text editor
4. Verify format matches: `GroupName: 1234 (+56)`

---

## Stage 5: Automation Test (Optional, 10 minutes)

Test the automated collection script:

### 5.1 Test Collection Script
```bash
source venv/bin/activate
python scripts/collect_data.py
```

**Expected:**
- Runs Selenium mode (slower)
- Collects data for all groups
- Saves to database
- Prints success/failure report

### 5.2 Verify Data Was Added
```bash
python3 -c "
from src.data.database import MemberDatabase
db = MemberDatabase()
data = db.get_all_data()
print(f'Collection timestamps: {data[\"timestamp\"].nunique()}')
db.close()
"
```

Should show 2 if you collected data twice.

---

## Troubleshooting Tests

### Scraper Test Fails

**Problem:** Network timeout
- **Fix:** Check internet connection
- **Fix:** Try from different network (VPN may help)

**Problem:** Can't find member count
- **Fix:** Normal for some regions, full scraper handles it
- **Fix:** Try Selenium mode: `MemberScraper(use_selenium=True)`

### Dashboard Won't Start

**Problem:** ModuleNotFoundError
- **Fix:** Activate venv: `source venv/bin/activate`
- **Fix:** Reinstall: `pip install -r requirements.txt`

**Problem:** Port already in use
- **Fix:** Stop other Streamlit instances
- **Fix:** Use different port: `streamlit run app.py --server.port 8502`

### No Data Shows in Dashboard

**Problem:** Database empty
- **Fix:** Click "Collect Data Now" first
- **Fix:** Wait for collection to complete

**Problem:** All scrapes failed
- **Fix:** Check internet connection
- **Fix:** Try again (intermittent network issues)
- **Fix:** Some groups may be temporarily down

### Selenium Errors

**Problem:** Chrome driver not found
- **Fix:** Install Chrome: `brew install --cask google-chrome`
- **Fix:** Update webdriver-manager: `pip install --upgrade webdriver-manager`

**Problem:** Selenium timeout
- **Fix:** Increase timeout in scraper.py
- **Fix:** Check internet speed
- **Fix:** Try non-Selenium mode for testing

---

## Test Checklist

Before deploying to GitHub Actions, verify:

- [ ] Pre-flight check passes
- [ ] Scraper test successfully fetches pages
- [ ] Setup completes without errors
- [ ] Dashboard starts and loads
- [ ] Manual collection works (at least some groups succeed)
- [ ] Charts display data correctly
- [ ] Copy-paste summary format is correct
- [ ] Database stores data persistently
- [ ] Time range filters work
- [ ] Individual group selection works
- [ ] Collection script runs successfully

## Next Steps After Testing

Once all tests pass:

1. **Commit to Git:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Conflux Member Tracker"
   ```

2. **Push to GitHub:**
   ```bash
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

3. **Enable GitHub Actions:**
   - Settings > Actions > General
   - Enable "Read and write permissions"

4. **Test GitHub Actions:**
   - Actions tab > "Bi-weekly Data Collection"
   - Click "Run workflow"
   - Check logs for success

5. **Verify Automation:**
   - Check that database was updated in repository
   - Pull changes: `git pull`
   - View updated data in dashboard

---

## Performance Benchmarks

Expected performance (approximate):

| Operation | Time | Notes |
|-----------|------|-------|
| Pre-flight check | <5s | System verification |
| Scraper test | 5-10s | Single group test |
| Full setup | 30-60s | Depends on internet speed |
| Manual collection (requests) | 15-20s | All 15 groups |
| Manual collection (Selenium) | 30-45s | Slower but more reliable |
| Dashboard startup | 2-5s | First load |
| Dashboard refresh | <1s | After data collection |

## Testing Frequency

- **During development**: Test after each major change
- **Before GitHub push**: Run full test suite
- **After GitHub Actions run**: Verify data collection worked
- **Monthly**: Verify scraper still works (sites may change)

---

## Getting Help

If tests fail:

1. Check [QUICKSTART.md](QUICKSTART.md) for basic setup
2. Check [README.md](README.md) troubleshooting section
3. Check [CLAUDE.md](CLAUDE.md) for technical details
4. Open GitHub issue with test output

Include in bug reports:
- Output of `./preflight_check.sh`
- Output of `python3 test_scraper.py`
- Error messages from dashboard
- Python version: `python3 --version`
- Operating system
