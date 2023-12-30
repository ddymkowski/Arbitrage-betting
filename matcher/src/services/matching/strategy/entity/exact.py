from src.schemas.consumer_match import FootballMatch
from src.services.matching.strategy.entity.base import \
    BaseEntityMatchingStrategy


class ExactEntityComparisonStrategy(BaseEntityMatchingStrategy):
    @staticmethod
    def match_entities(first_entity: FootballMatch, second_entity: FootballMatch):
        if first_entity.team_a_standardized != second_entity.team_a_standardized:
            return False

        if first_entity.team_b_standardized != second_entity.team_b_standardized:
            return False

        return True
