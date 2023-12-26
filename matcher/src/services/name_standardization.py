import json
import logging

from database import BASE_DIR
from src.schemas.consumer_match import FootballMatch

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s: %(message)s",
    level=logging.INFO,
)


class FootballClubNameStandardizationService:
    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__qualname__)
        self._mapping = self._load_synonyms_with_casefold()

    @staticmethod
    def _load_synonyms_with_casefold() -> dict[str, list[str]]:
        path = BASE_DIR / "src" / "services" / "resources" / "club_names_synonyms.json"
        with open(path) as f:
            synonyms = json.load(f)

        for standardized_club_name, variants in synonyms.items():
            synonyms[standardized_club_name] = [
                variant.casefold() for variant in variants
            ]

        return synonyms

    @staticmethod
    def _standardize_string(text: str) -> str:
        return text.strip().title()

    def standardize_club_names(self, football_event: FootballMatch) -> FootballMatch:
        standardized_club_name: str
        variants: list[str]
        for standardized_club_name, variants in self._mapping.items():
            if (
                not football_event.team_a_standardized
                and football_event.team_a.strip().casefold() in variants
            ):
                football_event.team_a_standardized = standardized_club_name
            if (
                not football_event.team_b_standardized
                and football_event.team_b.strip().casefold() in variants
            ):
                football_event.team_b_standardized = standardized_club_name

        football_event.team_a_standardized = (
            football_event.team_a_standardized
            or self._standardize_string(football_event.team_a)
        )
        football_event.team_b_standardized = (
            football_event.team_b_standardized
            or self._standardize_string(football_event.team_b)
        )

        return football_event
