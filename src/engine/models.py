from dataclasses import dataclass, field
from datetime import datetime

from src.enums import Bookmaker, FootballOutcome, PotentialBetState


@dataclass
class Odds:
    odds: float
    last_update: datetime = None

    def __lt__(self, other):
        return self.odds < other.odds

    def __gt__(self, other):
        return self.odds > other.odds

    def __eq__(self, other):
        return self.odds == other.odds

    def __ne__(self, other):
        return self.odds != other.odds


@dataclass
class BetOptions:
    bookmaker_odds: dict[Bookmaker, Odds]

    def get_bookmaker_with_highest_odd(self) -> dict[Bookmaker, Odds]:
        max_bookmaker, max_odd = max(
            self.bookmaker_odds.items(),
            key=lambda key_values_tpl: key_values_tpl[1].odds,
        )
        return {max_bookmaker: max_odd}


@dataclass
class Bet:
    outcome: FootballOutcome
    bookmaker: Bookmaker
    bet_amount: float
    odds: Odds


@dataclass
class BetsSet:
    state: PotentialBetState = PotentialBetState.RAW
    bets: tuple[Bet] = field(default_factory=tuple)

    def get_total_bets_amount(self):
        return sum([bet.bet_amount for bet in self.bets])

    def get_win_per_bet(self):
        return [bet.bet_amount * bet.odds.odds for bet in self.bets]

    def get_probability(self):
        return sum([1 / bet.odds.odds for bet in self.bets])


@dataclass
class Opportunity:
    exists: bool
    best_bet_option: dict[FootballOutcome, dict[Bookmaker, Odds]]
    profit: float = None


@dataclass
class FootballMatch:
    event_time: datetime
    team_a: str
    team_b: str
    bet_options: dict[FootballOutcome, BetOptions]

    def get_highest_odds(self) -> dict[FootballOutcome, dict[Bookmaker, Odds]]:
        results = {}
        for outcome, bet_option in self.bet_options.items():
            results[outcome] = bet_option.get_bookmaker_with_highest_odd()

        return results
