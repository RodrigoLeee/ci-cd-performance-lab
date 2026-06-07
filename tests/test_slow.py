import time
import pytest
from tests.experiment_config import ENABLE_SLOW_TESTS, SLOW_SLEEP_SECONDS, ENABLE_FAILING_TEST
from src.calculator import FinancialCalculator
from src.portfolio import Portfolio


@pytest.mark.skipif(not ENABLE_SLOW_TESTS, reason="Slow tests disabled")
def test_slow_compound_interest():
    """Simula processamento lento de cálculo em lote."""
    time.sleep(SLOW_SLEEP_SECONDS)
    calc = FinancialCalculator()
    results = [calc.compound_interest(1000 * i, 0.05, 10) for i in range(1, 11)]
    assert len(results) == 10
    assert all(r > 0 for r in results)


@pytest.mark.skipif(not ENABLE_SLOW_TESTS, reason="Slow tests disabled")
def test_slow_portfolio_simulation():
    """Simula construção lenta de portfólio com muitos ativos."""
    time.sleep(SLOW_SLEEP_SECONDS)
    portfolio = Portfolio()
    for i in range(20):
        portfolio.add_asset(f"ASSET{i:02d}", float(1000 * (i + 1)), 1.0 / 20)
    assert portfolio.total_value() == pytest.approx(210000.0, rel=1e-3)


def test_intentional_failure():
    """Este teste falha quando ENABLE_FAILING_TEST=True (experimento 6)."""
    if ENABLE_FAILING_TEST:
        pytest.fail("Falha intencional para o experimento 6 — teste propositalmente quebrado.")
    assert True
