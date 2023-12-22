from src.matcher.schemas import EntityMatcherModel
from src.matcher.strategy.entity.base import BaseEntityMatchingStrategy


class NaiveEntityMatchingStrategy(BaseEntityMatchingStrategy):
    def match_entities(self, first_entity: EntityMatcherModel, second_entity: EntityMatcherModel) -> bool:
        if first_entity.match_data.event_time != second_entity.match_data.event_time:
            return False

        if first_entity.match_data.team_a.casefold() != second_entity.match_data.team_a.casefold():
            return False

        if first_entity.match_data.team_b.casefold() != second_entity.match_data.team_b.casefold():
            return False

        return True
