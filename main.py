import asyncio

from src.utils.scraper import main, run_schedule_scrape

if __name__ == "__main__":
    response = asyncio.run(run_schedule_scrape())
