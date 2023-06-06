import logging
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.scrapers.betclic import main as betclic_scrape_job
from typing import Callable


class ScrapeJobsScheduler:
    def __init__(self, scrapping_jobs: list[Callable]):
        self._scheduler = AsyncIOScheduler()
        self._scrapping_jobs = scrapping_jobs

    def start_scheduler(self):
        for job in self._scrapping_jobs:
            self._scheduler.add_job(job, 'interval', seconds=1)

        self._scheduler.start()
        asyncio.get_event_loop().run_forever()


if __name__ == "__main__":
    jobs = [betclic_scrape_job]
    scheduler = ScrapeJobsScheduler(jobs)
    scheduler.start_scheduler()