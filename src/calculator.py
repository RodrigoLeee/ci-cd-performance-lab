import statistics
from src.validator import FinancialValidator


class FinancialCalculator:
    """Financial calculations for investment and loan analysis."""

    def compound_interest(self, principal: float, rate: float, periods: int) -> float:
        """Calculate compound interest: principal * (1 + rate)^periods."""
        FinancialValidator.validate_positive(principal, "principal")
        FinancialValidator.validate_rate(rate)
        FinancialValidator.validate_period(periods)
        return round(principal * (1 + rate) ** periods, 2)

    def present_value(self, future_value: float, rate: float, periods: int) -> float:
        """Calculate present value: future_value / (1 + rate)^periods."""
        FinancialValidator.validate_positive(future_value, "future_value")
        FinancialValidator.validate_rate(rate)
        FinancialValidator.validate_period(periods)
        if rate == -1.0:
            raise ValueError("Rate cannot be -1.0 (division by zero).")
        return round(future_value / (1 + rate) ** periods, 2)

    def future_value(self, present_value: float, rate: float, periods: int) -> float:
        """Calculate future value: present_value * (1 + rate)^periods."""
        FinancialValidator.validate_positive(present_value, "present_value")
        FinancialValidator.validate_rate(rate)
        FinancialValidator.validate_period(periods)
        return round(present_value * (1 + rate) ** periods, 2)

    def annuity_payment(self, principal: float, rate: float, periods: int) -> float:
        """Calculate Price annuity payment (loan installment)."""
        FinancialValidator.validate_positive(principal, "principal")
        FinancialValidator.validate_rate(rate)
        FinancialValidator.validate_period(periods)
        if rate == 0:
            return round(principal / periods, 2)
        numerator = principal * rate * (1 + rate) ** periods
        denominator = (1 + rate) ** periods - 1
        if denominator == 0:
            raise ValueError("Denominator is zero; check rate and periods.")
        return round(numerator / denominator, 2)

    def roi(self, gain: float, cost: float) -> float:
        """Calculate return on investment: (gain - cost) / cost * 100."""
        FinancialValidator.validate_positive(cost, "cost")
        if gain < 0:
            raise ValueError("gain must be non-negative.")
        return round((gain - cost) / cost * 100, 2)

    def cagr(self, start_value: float, end_value: float, periods: int) -> float:
        """Calculate compound annual growth rate."""
        FinancialValidator.validate_positive(start_value, "start_value")
        FinancialValidator.validate_positive(end_value, "end_value")
        FinancialValidator.validate_period(periods)
        return round((end_value / start_value) ** (1 / periods) - 1, 2)

    def sharpe_ratio(self, returns: list, risk_free_rate: float) -> float:
        """Calculate simplified Sharpe ratio: (mean_return - risk_free) / std_dev."""
        FinancialValidator.validate_list_not_empty(returns, "returns")
        if len(returns) < 2:
            raise ValueError("returns must have at least 2 elements to compute std dev.")
        FinancialValidator.validate_rate(risk_free_rate)
        mean_ret = statistics.mean(returns)
        std_dev = statistics.stdev(returns)
        if std_dev == 0:
            raise ValueError("Standard deviation of returns is zero; Sharpe undefined.")
        return round((mean_ret - risk_free_rate) / std_dev, 2)

    def weighted_average(self, values: list, weights: list) -> float:
        """Calculate weighted average of values."""
        FinancialValidator.validate_list_not_empty(values, "values")
        FinancialValidator.validate_list_not_empty(weights, "weights")
        if len(values) != len(weights):
            raise ValueError("values and weights must have the same length.")
        FinancialValidator.validate_weights_sum(weights)
        total = sum(v * w for v, w in zip(values, weights))
        return round(total, 2)

    def break_even(
        self, fixed_costs: float, price_per_unit: float, variable_cost_per_unit: float
    ) -> float:
        """Calculate break-even point in units."""
        FinancialValidator.validate_positive(fixed_costs, "fixed_costs")
        FinancialValidator.validate_positive(price_per_unit, "price_per_unit")
        if variable_cost_per_unit < 0:
            raise ValueError("variable_cost_per_unit must be non-negative.")
        margin = price_per_unit - variable_cost_per_unit
        if margin <= 0:
            raise ValueError(
                "price_per_unit must be greater than variable_cost_per_unit."
            )
        return round(fixed_costs / margin, 2)

    def npv(self, rate: float, cashflows: list) -> float:
        """Calculate net present value of a series of cashflows."""
        FinancialValidator.validate_cashflows(cashflows)
        FinancialValidator.validate_rate(rate)
        if rate == -1.0:
            raise ValueError("Rate cannot be -1.0 (division by zero).")
        total = 0.0
        for t, cf in enumerate(cashflows):
            total += cf / (1 + rate) ** t
        return round(total, 2)
