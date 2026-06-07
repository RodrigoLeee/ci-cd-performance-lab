class FinancialValidator:
    """Static validators for financial calculations."""

    @staticmethod
    def validate_rate(rate: float) -> None:
        """Rate must be a float between -1.0 and 100.0."""
        if not isinstance(rate, (int, float)):
            raise ValueError(f"rate must be numeric, got {type(rate).__name__}.")
        if rate < -1.0 or rate > 100.0:
            raise ValueError(f"rate must be between -1.0 and 100.0, got {rate}.")

    @staticmethod
    def validate_positive(value: float, name: str) -> None:
        """Value must be strictly positive."""
        if value <= 0:
            raise ValueError(f"{name} must be positive, got {value}.")

    @staticmethod
    def validate_period(periods: int) -> None:
        """Periods must be a positive integer."""
        if not isinstance(periods, int):
            raise ValueError(f"periods must be int, got {type(periods).__name__}.")
        if periods <= 0:
            raise ValueError(f"periods must be > 0, got {periods}.")

    @staticmethod
    def validate_list_not_empty(lst: list, name: str) -> None:
        """List must not be empty."""
        if not lst:
            raise ValueError(f"{name} must not be empty.")

    @staticmethod
    def validate_weights_sum(weights: list) -> None:
        """Sum of weights must be approximately 1.0."""
        total = sum(weights)
        if abs(total - 1.0) > 1e-6:
            raise ValueError(
                f"Weights must sum to 1.0, got {total:.6f}."
            )

    @staticmethod
    def validate_cashflows(cashflows: list) -> None:
        """Cashflows must have at least one element."""
        if not cashflows:
            raise ValueError("cashflows must have at least 1 element.")

    @staticmethod
    def is_valid_cpf(cpf: str) -> bool:
        """Validate Brazilian CPF using check-digit algorithm."""
        digits = "".join(filter(str.isdigit, cpf))
        if len(digits) != 11:
            return False
        if len(set(digits)) == 1:
            return False

        def calc_digit(d, weights):
            s = sum(int(d[i]) * weights[i] for i in range(len(weights)))
            remainder = s % 11
            return 0 if remainder < 2 else 11 - remainder

        weights1 = list(range(10, 1, -1))
        weights2 = list(range(11, 1, -1))
        d1 = calc_digit(digits, weights1)
        d2 = calc_digit(digits, weights2)
        return digits[9] == str(d1) and digits[10] == str(d2)

    @staticmethod
    def is_valid_cnpj(cnpj: str) -> bool:
        """Validate Brazilian CNPJ using check-digit algorithm."""
        digits = "".join(filter(str.isdigit, cnpj))
        if len(digits) != 14:
            return False
        if len(set(digits)) == 1:
            return False

        def calc_digit(d, length):
            weights = list(range(length + 1, 1, -1))
            # CNPJ weights cycle: for 13-digit check uses 5,4,3,2,9,8,7,6,5,4,3,2
            if length == 12:
                weights = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            else:
                weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
            s = sum(int(d[i]) * weights[i] for i in range(length))
            remainder = s % 11
            return 0 if remainder < 2 else 11 - remainder

        d1 = calc_digit(digits, 12)
        d2 = calc_digit(digits, 13)
        return digits[12] == str(d1) and digits[13] == str(d2)

    @staticmethod
    def format_currency(value: float, symbol: str = "R$") -> str:
        """Format a float as currency string."""
        formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{symbol} {formatted}"
