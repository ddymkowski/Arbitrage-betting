import logging
from math import ceil
from pprint import pformat
from typing import Optional

from models import Bet, BetsSet, FootballMatch, Odds, Opportunity

from src.enums import Bookmaker, FootballOutcome, PotentialBetState

logging.basicConfig(
    format="%(asctime)s | %(name)s | %(funcName)s | %(levelname)s: %(message)s",
    level=logging.INFO,
)


# TODO add profit check after masking
# TODO add arbitrage masker a safecheck to not go beyond initial bet value


class ArbitrageMasker:
    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

    @staticmethod
    def _round_to_nearest_multiple_of_x(
        value_to_round: float,
        multiplier_value: int,
        round_up: bool = True,
    ) -> float:
        rounded_value = float(
            ceil(value_to_round / multiplier_value) * multiplier_value
        )

        if not round_up:
            return rounded_value - multiplier_value
        return rounded_value

    def apply_arbitrage_masking(self, bets_to_place: BetsSet) -> BetsSet:
        for bet in bets_to_place.bets:
            bet.bet_amount = self._round_to_nearest_multiple_of_x(bet.bet_amount, 50)
        bets_to_place.state = PotentialBetState.MASKED

        return bets_to_place


class StakeCalculator:
    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

    def calculate_perfect_stake(
        self,
        best_betting_options: dict[FootballOutcome, dict[Bookmaker, Odds]],
        expected_win_amount: float,
    ) -> BetsSet:
        results = BetsSet()
        for outcome, bookmaker_odds in best_betting_options.items():
            for bookmaker, odds in bookmaker_odds.items():
                results.bets += (
                    Bet(
                        outcome=outcome,
                        bookmaker=bookmaker,
                        bet_amount=round(expected_win_amount / odds.odds, 2),
                        odds=odds,
                    ),
                )

        self._logger.info(
            "Options to place for the potential arbitrage opportunity are:"
            f" {pformat(results)}\n"
        )
        return results


class BetRequestHandler:
    def __init__(self) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)

    def send_place_bet_request(self, *args, **kwargs):
        self._logger.info(f"Sending request to bet - bet details: {args} {kwargs}\n")


class ArbitrageEngine:
    def __init__(
        self,
        masker: Optional[ArbitrageMasker] = None,
        bet_request_handler: Optional[BetRequestHandler] = None,
        stake_calculator: Optional[StakeCalculator] = None,
    ) -> None:
        self._logger = logging.getLogger(self.__class__.__name__)
        self._masker = masker or ArbitrageMasker()
        self._bet_request_handler = bet_request_handler or BetRequestHandler()
        self._stake_calculator = stake_calculator or StakeCalculator()

    def process_event(self, event: FootballMatch, expected_winning: float) -> None:
        arbitrage_opportunity = self._calculate_raw_opportunity(event)

        if not arbitrage_opportunity.exists:
            return None

        self._handle_existing_opportunity(arbitrage_opportunity, expected_winning)

        if not arbitrage_opportunity.profit:
            self._logger.info(
                "No profit after masking for"
                f" {pformat(arbitrage_opportunity.best_bet_option)}\n"
            )
            return None

        self._logger.info(
            "Expected profit with"
            f" {pformat(arbitrage_opportunity.best_bet_option)} is"
            f" {arbitrage_opportunity.profit}\n"
        )
        self._bet_request_handler.send_place_bet_request()

    def _handle_existing_opportunity(
        self,
        arbitrage_opportunity: Opportunity,
        expected_winning: float,
    ) -> Optional[float]:
        bets_to_place = self._stake_calculator.calculate_perfect_stake(
            arbitrage_opportunity.best_bet_option,
            expected_winning,
        )

        bets_to_place_masked = self._masker.apply_arbitrage_masking(bets_to_place)
        self._logger.info(f"Betting options masked:\n{pformat(bets_to_place_masked)}\n")

        total_bet_value_masked = bets_to_place_masked.get_total_bets_amount()
        print(bets_to_place_masked.get_win_per_bet())
        print("~~" * 10)
        arbitrage_opportunity.profit = self._check_for_profit(
            total_bet_value_masked,
            expected_winning,
        )

    @staticmethod
    def _check_for_profit(bet_value: float, expected_winning: float) -> float:
        profit = expected_winning - bet_value
        if profit > 0:
            return profit
        return None

    def _calculate_raw_opportunity(self, event: FootballMatch) -> Opportunity:
        best_betting_options = event.get_highest_odds()
        probability = self._calculate_odds_probabilities(best_betting_options)
        opportunity = self._check_arbitrage_opportunity(probability)

        return Opportunity(
            exists=opportunity,
            best_bet_option=best_betting_options,
        )

    @staticmethod
    def _calculate_odds_probabilities(
        best_betting_options: dict[FootballOutcome, dict[Bookmaker, Odds]]
    ) -> float:
        probability = 0.0
        for bookmaker in best_betting_options.values():
            for odds in bookmaker.values():
                probability += 1 / odds.odds
        return probability

    @staticmethod
    def _check_arbitrage_opportunity(probability: float) -> bool:
        return probability < 1.0
