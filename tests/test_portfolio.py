import pytest
from src.portfolio import Portfolio


@pytest.fixture
def empty_portfolio():
    return Portfolio()


@pytest.fixture
def simple_portfolio():
    p = Portfolio()
    p.add_asset("PETR4", 5000.0, 0.5)
    p.add_asset("VALE3", 3000.0, 0.3)
    p.add_asset("ITUB4", 2000.0, 0.2)
    return p


# ── add_asset / remove_asset ──────────────────────────────────────────────────

def test_add_asset_normal(empty_portfolio):
    empty_portfolio.add_asset("AAPL", 1000.0, 1.0)
    assert empty_portfolio.total_value() == 1000.0


def test_add_asset_duplicate(simple_portfolio):
    with pytest.raises(ValueError):
        simple_portfolio.add_asset("PETR4", 100.0, 0.1)


def test_add_asset_invalid_weight(empty_portfolio):
    with pytest.raises(ValueError):
        empty_portfolio.add_asset("X", 100.0, 0.0)


def test_remove_asset_normal(simple_portfolio):
    simple_portfolio.remove_asset("PETR4")
    assert simple_portfolio.total_value() == 5000.0


def test_remove_asset_not_found(simple_portfolio):
    with pytest.raises(ValueError):
        simple_portfolio.remove_asset("NOPE")


# ── total_value ───────────────────────────────────────────────────────────────

def test_total_value_empty(empty_portfolio):
    assert empty_portfolio.total_value() == 0.0


def test_total_value_multiple(simple_portfolio):
    assert simple_portfolio.total_value() == 10000.0


# ── weighted_return ───────────────────────────────────────────────────────────

def test_weighted_return_normal(simple_portfolio):
    returns = {"PETR4": 0.1, "VALE3": 0.2, "ITUB4": -0.05}
    result = simple_portfolio.weighted_return(returns)
    expected = 0.5 * 0.1 + 0.3 * 0.2 + 0.2 * (-0.05)
    assert result == pytest.approx(expected, abs=0.001)


def test_weighted_return_empty_portfolio(empty_portfolio):
    with pytest.raises(ValueError):
        empty_portfolio.weighted_return({})


def test_weighted_return_missing_asset(simple_portfolio):
    with pytest.raises(ValueError):
        simple_portfolio.weighted_return({"PETR4": 0.1})


# ── diversification_index ─────────────────────────────────────────────────────

def test_diversification_index_equal_weights():
    p = Portfolio()
    p.add_asset("A", 100.0, 0.5)
    p.add_asset("B", 100.0, 0.5)
    result = p.diversification_index()
    assert result == 1.0


def test_diversification_index_single_asset(empty_portfolio):
    empty_portfolio.add_asset("A", 1000.0, 1.0)
    result = empty_portfolio.diversification_index()
    assert result == 0.0


# ── rebalance ─────────────────────────────────────────────────────────────────

def test_rebalance_normal(simple_portfolio):
    target = {"PETR4": 0.4, "VALE3": 0.4, "ITUB4": 0.2}
    adjustments = simple_portfolio.rebalance(target)
    assert adjustments["PETR4"] == pytest.approx(-1000.0, abs=0.01)
    assert adjustments["VALE3"] == pytest.approx(1000.0, abs=0.01)
    assert adjustments["ITUB4"] == pytest.approx(0.0, abs=0.01)


def test_rebalance_missing_target(simple_portfolio):
    with pytest.raises(ValueError):
        simple_portfolio.rebalance({"PETR4": 0.5})


# ── risk_exposure ─────────────────────────────────────────────────────────────

def test_risk_exposure_normal(simple_portfolio):
    vols = {"PETR4": 0.3, "VALE3": 0.25, "ITUB4": 0.2}
    result = simple_portfolio.risk_exposure(vols)
    expected = 0.5 * 0.3 + 0.3 * 0.25 + 0.2 * 0.2
    assert result == pytest.approx(expected, abs=0.001)


def test_risk_exposure_empty(empty_portfolio):
    with pytest.raises(ValueError):
        empty_portfolio.risk_exposure({})


# ── to_dict / summary ─────────────────────────────────────────────────────────

def test_to_dict(simple_portfolio):
    d = simple_portfolio.to_dict()
    assert d["asset_count"] == 3
    assert d["total_value"] == 10000.0
    assert len(d["assets"]) == 3


def test_summary_empty(empty_portfolio):
    assert "empty" in empty_portfolio.summary().lower()


def test_summary_normal(simple_portfolio):
    s = simple_portfolio.summary()
    assert "PETR4" in s
    assert "10,000.00" in s or "10000" in s
