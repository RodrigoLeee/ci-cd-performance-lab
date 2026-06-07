import pytest
from tests.experiment_config import EXTRA_TEST_MULTIPLIER
from src.calculator import FinancialCalculator

# ── compound_interest ─────────────────────────────────────────────────────────

COMPOUND_BASE = [
    (1000, 0.1, 1, 1100.0),
    (1000, 0.1, 2, 1210.0),
    (5000, 0.05, 3, 5788.13),
    (10000, 0.12, 5, 17623.42),
    (500, 0.08, 10, 1079.46),
]

COMPOUND_CASES = COMPOUND_BASE * EXTRA_TEST_MULTIPLIER


@pytest.mark.parametrize("principal,rate,periods,expected", COMPOUND_CASES)
def test_compound_interest_parametrized(principal, rate, periods, expected):
    calc = FinancialCalculator()
    assert calc.compound_interest(principal, rate, periods) == pytest.approx(expected, abs=0.01)


# ── present_value ─────────────────────────────────────────────────────────────

PRESENT_VALUE_BASE = [
    (1100.0, 0.1, 1, 1000.0),
    (1210.0, 0.1, 2, 1000.0),
    (5788.13, 0.05, 3, 5000.0),
    (17623.42, 0.12, 5, 10000.0),
    (1079.46, 0.08, 10, 500.0),
]

PRESENT_VALUE_CASES = PRESENT_VALUE_BASE * EXTRA_TEST_MULTIPLIER


@pytest.mark.parametrize("fv,rate,periods,expected", PRESENT_VALUE_CASES)
def test_present_value_parametrized(fv, rate, periods, expected):
    calc = FinancialCalculator()
    assert calc.present_value(fv, rate, periods) == pytest.approx(expected, rel=0.01)


# ── roi ───────────────────────────────────────────────────────────────────────

ROI_BASE = [
    (1500, 1000, 50.0),
    (2000, 1000, 100.0),
    (750, 1000, -25.0),
    (1100, 1000, 10.0),
    (3000, 2000, 50.0),
]

ROI_CASES = ROI_BASE * EXTRA_TEST_MULTIPLIER


@pytest.mark.parametrize("gain,cost,expected", ROI_CASES)
def test_roi_parametrized(gain, cost, expected):
    calc = FinancialCalculator()
    assert calc.roi(gain, cost) == pytest.approx(expected, abs=0.01)


# ── npv ───────────────────────────────────────────────────────────────────────

NPV_BASE = [
    (0.10, [-1000, 300, 400, 500], -21.04),
    (0.0, [-1000, 400, 400, 400], 200.0),
    (0.05, [-500, 200, 200, 200], 44.65),
    (0.08, [-2000, 800, 800, 800], 61.64),
    (0.12, [-5000, 2200, 2200, 2200], 284.04),
]

NPV_CASES = NPV_BASE * EXTRA_TEST_MULTIPLIER


@pytest.mark.parametrize("rate,cashflows,expected", NPV_CASES)
def test_npv_parametrized(rate, cashflows, expected):
    calc = FinancialCalculator()
    assert calc.npv(rate, cashflows) == pytest.approx(expected, abs=1.0)
