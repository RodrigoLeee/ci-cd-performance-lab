import pytest
from src.validator import FinancialValidator


# ── validate_rate ─────────────────────────────────────────────────────────────

def test_validate_rate_valid():
    FinancialValidator.validate_rate(0.05)  # no exception


def test_validate_rate_zero():
    FinancialValidator.validate_rate(0.0)


def test_validate_rate_above_max():
    with pytest.raises(ValueError):
        FinancialValidator.validate_rate(101.0)


def test_validate_rate_below_min():
    with pytest.raises(ValueError):
        FinancialValidator.validate_rate(-1.5)


# ── validate_positive ─────────────────────────────────────────────────────────

def test_validate_positive_valid():
    FinancialValidator.validate_positive(1.0, "x")


def test_validate_positive_zero():
    with pytest.raises(ValueError):
        FinancialValidator.validate_positive(0, "x")


def test_validate_positive_negative():
    with pytest.raises(ValueError):
        FinancialValidator.validate_positive(-5.0, "amount")


# ── validate_period ───────────────────────────────────────────────────────────

def test_validate_period_valid():
    FinancialValidator.validate_period(12)


def test_validate_period_zero():
    with pytest.raises(ValueError):
        FinancialValidator.validate_period(0)


def test_validate_period_not_int():
    with pytest.raises(ValueError):
        FinancialValidator.validate_period(1.5)


# ── validate_list_not_empty ───────────────────────────────────────────────────

def test_validate_list_not_empty_valid():
    FinancialValidator.validate_list_not_empty([1, 2, 3], "data")


def test_validate_list_not_empty_empty():
    with pytest.raises(ValueError):
        FinancialValidator.validate_list_not_empty([], "data")


# ── validate_weights_sum ──────────────────────────────────────────────────────

def test_validate_weights_sum_valid():
    FinancialValidator.validate_weights_sum([0.25, 0.5, 0.25])


def test_validate_weights_sum_invalid():
    with pytest.raises(ValueError):
        FinancialValidator.validate_weights_sum([0.5, 0.3])


# ── validate_cashflows ────────────────────────────────────────────────────────

def test_validate_cashflows_valid():
    FinancialValidator.validate_cashflows([-1000, 500])


def test_validate_cashflows_empty():
    with pytest.raises(ValueError):
        FinancialValidator.validate_cashflows([])


# ── is_valid_cpf ──────────────────────────────────────────────────────────────

def test_cpf_valid():
    # Known valid CPF
    assert FinancialValidator.is_valid_cpf("529.982.247-25") is True


def test_cpf_valid_digits_only():
    assert FinancialValidator.is_valid_cpf("52998224725") is True


def test_cpf_invalid_check_digits():
    assert FinancialValidator.is_valid_cpf("529.982.247-26") is False


def test_cpf_all_same_digits():
    assert FinancialValidator.is_valid_cpf("111.111.111-11") is False


def test_cpf_wrong_length():
    assert FinancialValidator.is_valid_cpf("123.456.789") is False


# ── is_valid_cnpj ─────────────────────────────────────────────────────────────

def test_cnpj_valid():
    # Known valid CNPJ
    assert FinancialValidator.is_valid_cnpj("11.222.333/0001-81") is True


def test_cnpj_valid_digits_only():
    assert FinancialValidator.is_valid_cnpj("11222333000181") is True


def test_cnpj_invalid_check_digit():
    assert FinancialValidator.is_valid_cnpj("11.222.333/0001-82") is False


def test_cnpj_all_same_digits():
    assert FinancialValidator.is_valid_cnpj("00000000000000") is False


# ── format_currency ───────────────────────────────────────────────────────────

def test_format_currency_default_symbol():
    result = FinancialValidator.format_currency(1234.56)
    assert result == "R$ 1.234,56"


def test_format_currency_custom_symbol():
    result = FinancialValidator.format_currency(1000.0, "$")
    assert result == "$ 1.000,00"


def test_format_currency_small_value():
    result = FinancialValidator.format_currency(0.99)
    assert result == "R$ 0,99"
