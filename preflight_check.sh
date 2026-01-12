#!/bin/bash
# Pre-flight check before running the application

echo "🔍 Pre-flight System Check"
echo "="
echo ""

# Check 1: Xcode Command Line Tools
echo "1️⃣  Checking Xcode Command Line Tools..."
if xcode-select -p &> /dev/null; then
    echo "   ✅ Xcode Command Line Tools installed"

    # Check if license is accepted
    if ! python3 --version &> /dev/null; then
        echo "   ⚠️  Xcode license not accepted"
        echo ""
        echo "   ACTION REQUIRED:"
        echo "   Run this command to accept the license:"
        echo "   sudo xcodebuild -license"
        echo ""
        exit 1
    else
        PYTHON_VERSION=$(python3 --version 2>&1)
        echo "   ✅ Xcode license accepted"
        echo "   ✅ $PYTHON_VERSION available"
    fi
else
    echo "   ❌ Xcode Command Line Tools not installed"
    echo ""
    echo "   ACTION REQUIRED:"
    echo "   Run this command to install:"
    echo "   xcode-select --install"
    echo ""
    exit 1
fi

echo ""

# Check 2: Python version
echo "2️⃣  Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 11 ]; then
    echo "   ✅ Python $PYTHON_VERSION (meets requirement: 3.11+)"
else
    echo "   ⚠️  Python $PYTHON_VERSION (recommended: 3.11+)"
    echo "   The app may still work, but consider upgrading"
    echo ""
    echo "   To upgrade Python:"
    echo "   brew install python@3.11"
    echo ""
fi

echo ""

# Check 3: Internet connectivity
echo "3️⃣  Checking internet connectivity..."
if ping -c 1 google.com &> /dev/null; then
    echo "   ✅ Internet connection working"
else
    echo "   ⚠️  No internet connection detected"
    echo "   Web scraping requires internet access"
fi

echo ""

# Check 4: Chrome/Chromium (optional for Selenium)
echo "4️⃣  Checking Chrome browser (optional)..."
if [ -d "/Applications/Google Chrome.app" ]; then
    echo "   ✅ Google Chrome installed"
    echo "   (Selenium web scraping will work)"
elif [ -d "/Applications/Chromium.app" ]; then
    echo "   ✅ Chromium installed"
    echo "   (Selenium web scraping will work)"
else
    echo "   ⚠️  Chrome not found"
    echo "   Basic scraping will work, but Selenium mode requires Chrome"
    echo ""
    echo "   To install Chrome:"
    echo "   brew install --cask google-chrome"
    echo "   OR download from: https://www.google.com/chrome/"
fi

echo ""
echo "="
echo "✅ Pre-flight check complete!"
echo ""
echo "Next steps:"
echo "  1. Fix any issues shown above (if any)"
echo "  2. Run test: python3 test_scraper.py"
echo "  3. Run setup: ./setup.sh"
echo "  4. Start app: streamlit run app.py"
echo ""
