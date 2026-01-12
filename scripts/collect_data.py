#!/usr/bin/env python3
"""
Automated data collection script for GitHub Actions
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data.scraper import MemberScraper
from src.data.database import MemberDatabase


def main():
    """Run data collection"""
    print("Starting data collection...")

    # Initialize scraper with Selenium for GitHub Actions
    scraper = MemberScraper(use_selenium=True)

    # Scrape all groups
    print("Scraping Telegram groups and Discord...")
    counts = scraper.scrape_all()

    # Filter successful scrapes
    successful = {k: v for k, v in counts.items() if v is not None}
    failed = [k for k, v in counts.items() if v is None]

    # Save to database
    if successful:
        db = MemberDatabase()
        db.add_member_counts(successful)
        db.close()

        print(f"\n✅ Successfully collected data for {len(successful)} groups:")
        for name, count in successful.items():
            print(f"  - {name}: {count:,} members")

    if failed:
        print(f"\n⚠️  Failed to scrape {len(failed)} groups:")
        for name in failed:
            print(f"  - {name}")

    # Exit with error if all scrapes failed
    if not successful:
        print("\n❌ All scrapes failed!")
        sys.exit(1)

    print("\n✅ Data collection complete!")


if __name__ == "__main__":
    main()
