"""
Web scraper for Telegram and Discord member counts
"""
import re
import time
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class MemberScraper:
    """Scrapes member counts from Telegram and Discord"""

    # Group configuration with display names
    TELEGRAM_GROUPS = {
        "Africa (TG)": "https://t.me/ConfluxAfrica",
        "Arabic (TG)": "https://t.me/confluxarabic/",
        "China Official (TG)": "https://t.me/Conflux_Chinese",
        "China Web3 Community (TG)": "https://t.me/ConfluxWeb3China",
        "English (TG)": "https://t.me/Conflux_English",
        "French (TG)": "https://t.me/ConfluxFrench",
        "Indonesia (TG)": "https://t.me/Conflux_indonesia",
        "Korea (TG)": "https://t.me/ConfluxKorea",
        "LATAM (TG)": "https://t.me/Conflux_LATAM",
        "Persia (TG)": "https://t.me/ConfluxPersian1",
        "Russian (TG)": "https://t.me/confluxrussian",
        "Turkey (TG)": "https://t.me/Conflux_Turkish",
        "Ukraine (TG)": "https://t.me/Conflux_Ukraine",
        "Vietnam (TG)": "https://t.me/confluxvietnam",
    }

    DISCORD_SERVER = "https://discord.com/invite/confluxnetwork"
    DISCORD_NAME = "English (Discord)"

    def __init__(self, use_selenium: bool = False):
        """
        Initialize the scraper

        Args:
            use_selenium: If True, use Selenium for JavaScript-rendered pages
        """
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape_telegram_group(self, url: str) -> Optional[int]:
        """
        Scrape member count from a Telegram group

        Args:
            url: Telegram group URL

        Returns:
            Member count or None if scraping fails
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Look for member count in various possible locations
            # Telegram shows counts like "14 760 members", "1,234 members" or "1.2K subscribers"
            patterns = [
                r'([\d\s,]+)\s+members',  # Handles "14 760 members" or "1,234 members"
                r'([\d\s,]+)\s+subscribers',  # Handles "14 760 subscribers" or "1,234 subscribers"
                r'([\d.]+[KM])\s+members',  # Handles "1.2K members"
                r'([\d.]+[KM])\s+subscribers',  # Handles "1.2K subscribers"
            ]

            text = soup.get_text()

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    count_str = match.group(1).strip()
                    # Convert "1.2K" to 1200, "1.5M" to 1500000
                    if 'K' in count_str.upper():
                        return int(float(count_str.replace('K', '').replace(',', '').replace(' ', '')) * 1000)
                    elif 'M' in count_str.upper():
                        return int(float(count_str.replace('M', '').replace(',', '').replace(' ', '')) * 1000000)
                    else:
                        # Remove spaces, commas, and convert to int
                        return int(count_str.replace(',', '').replace(' ', ''))

            # If no pattern matches, try finding the count in meta tags or specific divs
            # This may need adjustment based on actual Telegram page structure
            member_div = soup.find('div', class_='tgme_page_extra')
            if member_div:
                match = re.search(r'([\d,]+)', member_div.get_text())
                if match:
                    return int(match.group(1).replace(',', ''))

            return None

        except Exception as e:
            print(f"Error scraping Telegram {url}: {e}")
            return None

    def scrape_discord_server(self) -> Optional[int]:
        """
        Scrape member count from Discord invite page
        Uses Discord Invite API (fast, no Selenium needed)

        Returns:
            Member count or None if scraping fails
        """
        # Try Discord Invite API first (fast, no auth needed)
        count = self._scrape_discord_api()
        if count:
            return count

        # Fallback to Selenium if API fails
        if self.use_selenium:
            return self._scrape_discord_selenium()

        return None

    def _scrape_discord_api(self) -> Optional[int]:
        """Scrape Discord using public Invite API (no auth needed)"""
        try:
            # Extract invite code from URL
            invite_code = self.DISCORD_SERVER.split('/')[-1]

            # Use Discord's public invite API
            url = f"https://discord.com/api/v10/invites/{invite_code}?with_counts=true"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()
            member_count = data.get('approximate_member_count', 0)

            if member_count > 0:
                return member_count

            return None

        except Exception as e:
            print(f"Error scraping Discord with API: {e}")
            return None

    def _scrape_discord_requests(self) -> Optional[int]:
        """Scrape Discord using requests (may not work if JS-rendered)"""
        try:
            response = self.session.get(self.DISCORD_SERVER, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Discord shows member count on invite pages
            # Look for patterns like "1,234 members" or "1,234 online"
            text = soup.get_text()

            patterns = [
                r'([\d,]+)\s+members',
                r'([\d,]+)\s+Members',
            ]

            for pattern in patterns:
                match = re.search(pattern, text)
                if match:
                    return int(match.group(1).replace(',', ''))

            return None

        except Exception as e:
            print(f"Error scraping Discord: {e}")
            return None

    def _scrape_discord_selenium(self) -> Optional[int]:
        """Scrape Discord using Selenium for JavaScript rendering"""
        driver = None
        try:
            # Set up Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

            # Initialize driver
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)

            # Load page
            driver.get(self.DISCORD_SERVER)

            # Wait for member count to load
            wait = WebDriverWait(driver, 10)
            # Adjust selector based on actual Discord page structure
            member_element = wait.until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'members')]"))
            )

            # Extract number
            text = member_element.text
            match = re.search(r'([\d,]+)', text)
            if match:
                return int(match.group(1).replace(',', ''))

            return None

        except Exception as e:
            print(f"Error scraping Discord with Selenium: {e}")
            return None
        finally:
            if driver:
                driver.quit()

    def scrape_all_telegram(self) -> Dict[str, Optional[int]]:
        """
        Scrape all Telegram groups

        Returns:
            Dictionary mapping group names to member counts
        """
        results = {}
        for name, url in self.TELEGRAM_GROUPS.items():
            print(f"Scraping {name}...")
            count = self.scrape_telegram_group(url)
            results[name] = count
            time.sleep(1)  # Be respectful, don't hammer servers

        return results

    def scrape_all(self) -> Dict[str, Optional[int]]:
        """
        Scrape all groups (Telegram + Discord)

        Returns:
            Dictionary mapping group names to member counts
        """
        results = self.scrape_all_telegram()

        print(f"Scraping {self.DISCORD_NAME}...")
        discord_count = self.scrape_discord_server()
        results[self.DISCORD_NAME] = discord_count

        return results


if __name__ == "__main__":
    # Test the scraper
    scraper = MemberScraper()
    results = scraper.scrape_all()

    print("\n--- Results ---")
    for name, count in results.items():
        if count:
            print(f"{name}: {count:,} members")
        else:
            print(f"{name}: Failed to scrape")
