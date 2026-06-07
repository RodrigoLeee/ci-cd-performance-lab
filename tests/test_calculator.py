import pytest
from src.calculator import FinancialCalculator


@pytest.fixture
def calc():
    return FinancialCalculator()


# ── compound_interest ──────────────────────────────────────────────────────────

def test_compound_interest_normal(calc):
    assert calc.compound_interest(1000, 0.1, 1) == 1100.0


def test_compound_interest_multiple_periods(calc):
    assert calc.compound_interest(1000, 0.1, 2) == 1210.0


def test_compound_interest_zero_rate(calc):
    assert calc.compound_interest(1000, 0.0, 5) == 1000.0


def test_compound_interest_invalid_principal(calc):
    with pytest.raises(ValueError):
        calc.compound_interest(-100, 0.1, 5)


def test_compound_interest_invalid_rate(calc):
    with pytest.raises(ValueError):
        calc.compound_interest(1000, -2.0, 5)


def test_compound_interest_invalid_period(calc):
    with pytest.raises(ValueError):
        calc.compound_interest(1000, 0.1, 0)


# ── present_value ─────────────────────────────────────────────────────────────

def test_present_value_normal(calc):
    assert calc.present_value(1100.0, 0.1, 1) == 1000.0


def test_present_value_period_1(calc):
    result = calc.present_value(1050.0, 0.05, 1)
    assert result == pytest.approx(1000.0, abs=0.01)


def test_present_value_invalid_rate(calc):
    with pytest.raises(ValueError):
        calc.present_value(1000, -2.0, 3)


# ── future_value ──────────────────────────────────────────────────────────────

def test_future_value_normal(calc):
    assert calc.future_value(1000, 0.1, 1) == 1100.0


def test_future_value_zero_rate(calc):
    assert calc.future_value(500, 0.0, 10) == 500.0


def test_future_value_invalid_pv(calc):
    with pytest.raises(ValueError):
        calc.future_value(0, 0.1, 5)


# ── annuity_payment ───────────────────────────────────────────────────────────

def test_annuity_payment_normal(calc):
    result = calc.annuity_payment(10000, 0.01, 12)
    assert result == pytest.approx(888.49, abs=0.01)


def test_annuity_payment_zero_rate(calc):
    result = calc.annuity_payment(1200, 0.0, 12)
    assert result == 100.0


def test_annuity_payment_invalid_principal(calc):
    with pytest.raises(ValueError):
        calc.annuity_payment(-1000, 0.05, 12)


# ── roi ───────────────────────────────────────────────────────────────────────

def test_roi_normal(calc):
    assert calc.roi(1500, 1000) == 50.0


def test_roi_zero_gain_less_than_cost(calc):
    assert calc.roi(500, 1000) == -50.0


def test_roi_invalid_cost(calc):
    with pytest.raises(ValueError):
        calc.roi(1000, 0)


def test_roi_negative_gain(calc):
    with pytest.raises(ValueError):
        calc.roi(-100, 1000)


# ── cagr ─────────────────────────────────────────────────────────────────────

def test_cagr_normal(calc):
    result = calc.cagr(1000, 1610.51, 10)
    assert result == pytest.approx(0.05, abs=0.01)


def test_cagr_one_period(calc):
    result = calc.cagr(1000, 1100, 1)
    assert result == pytest.approx(0.1, abs=0.01)


def test_cagr_invalid_start(calc):
    with pytest.raises(ValueError):
        calc.cagr(0, 1000, 5)


# ── sharpe_ratio ──────────────────────────────────────────────────────────────

def test_sharpe_ratio_normal(calc):
    returns = [0.1, 0.2, 0.15, 0.05, 0.12]
    result = calc.sharpe_ratio(returns, 0.02)
    assert isinstance(result, float)


def test_sharpe_ratio_single_element(calc):
    with pytest.raises(ValueError):
        calc.sharpe_ratio([0.1], 0.02)


def test_sharpe_ratio_empty(calc):
    with pytest.raises(ValueError):
        calc.sharpe_ratio([], 0.02)


# ── weighted_average ──────────────────────────────────────────────────────────

def test_weighted_average_normal(calc):
    result = calc.weighted_average([100, 200, 300], [0.25, 0.5, 0.25])
    assert result == 200.0


def test_weighted_average_equal_weights(calc):
    result = calc.weighted_average([10, 20], [0.5, 0.5])
    assert result == 15.0


def test_weighted_average_mismatched_lengths(calc):
    with pytest.raises(ValueError):
        calc.weighted_average([100, 200], [0.5, 0.3, 0.2])


# ── break_even ────────────────────────────────────────────────────────────────

def test_break_even_normal(calc):
    result = calc.break_even(10000, 50, 30)
    assert result == 500.0


def test_break_even_single_unit_margin(calc):
    result = calc.break_even(1000, 2, 1)
    assert result == 1000.0


def test_break_even_negative_margin(calc):
    with pytest.raises(ValueError):
        calc.break_even(1000, 10, 15)


# ── npv ──────────────────────────────────────────────────────────────────────

def test_npv_normal(calc):
    cashflows = [-1000, 300, 400, 500]
    result = calc.npv(0.1, cashflows)
    assert result == pytest.approx((-1000 + 300/1.1 + 400/1.21 + 500/1.331), abs=0.02)


def test_npv_zero_rate(calc):
    cashflows = [-1000, 400, 400, 400]
    result = calc.npv(0.0, cashflows)
    assert result == pytest.approx(200.0, abs=0.01)


def test_npv_empty_cashflows(calc):
    with pytest.raises(ValueError):
        calc.npv(0.1, [])
