from Levenshtein import ratio
from src.schemas.consumer_match import FootballMatch
from src.services.matching.strategy.entity.base import \
    BaseEntityMatchingStrategy


class LevenshteinDistanceEntityComparisonStrategy(BaseEntityMatchingStrategy):
    THRESHOLD = 0.8

    @staticmethod
    def preprocess(text: str) -> str:
        # TODO remove FC/F.C. case insensitive
        return text

    def match_entities(
        self, first_entity: FootballMatch, second_entity: FootballMatch
    ) -> bool:
        if (
            ratio(first_entity.team_a_standardized, second_entity.team_a_standardized)
            < self.THRESHOLD
        ):
            return False

        if (
            ratio(first_entity.team_b_standardized, second_entity.team_b_standardized)
            < self.THRESHOLD
        ):
            return False

        return True
