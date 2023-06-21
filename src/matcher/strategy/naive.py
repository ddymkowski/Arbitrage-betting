from src.matcher.strategy.base import BaseEntityMatchingStrategy, EntityMatcherModel


class NaiveMatchingStrategy(BaseEntityMatchingStrategy):
    def match_entities(self, first_entity: EntityMatcherModel, second_entity: EntityMatcherModel) -> bool:
        if first_entity.match_data.event_time != second_entity.match_data.event_time:
            return False

        if first_entity.match_data.team_a.casefold() != second_entity.match_data.team_a.casefold():
            return False

        if first_entity.match_data.team_b.casefold() != second_entity.match_data.team_b.casefold():
            return False

        return True
