from dataclasses import dataclass

from src.enums import Bookmaker

from scrapers.src.schemas import ScrapeResultModel, ScrapeResultModelEnriched

BookmakersDatasets = dict[Bookmaker, list[ScrapeResultModelEnriched]]


@dataclass
class EntityMatcherModel:
    bookmaker: Bookmaker
    match_data: ScrapeResultModel
