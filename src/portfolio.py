from src.validator import FinancialValidator


class Portfolio:
    """Represents an investment portfolio with assets and weights."""

    def __init__(self):
        self._assets = []  # list of dicts: {name, value, weight}

    def add_asset(self, name: str, value: float, weight: float) -> None:
        """Add an asset to the portfolio."""
        if not name or not isinstance(name, str):
            raise ValueError("name must be a non-empty string.")
        FinancialValidator.validate_positive(value, "value")
        if weight <= 0 or weight > 1:
            raise ValueError("weight must be between 0 (exclusive) and 1 (inclusive).")
        if any(a["name"] == name for a in self._assets):
            raise ValueError(f"Asset '{name}' already exists in portfolio.")
        self._assets.append({"name": name, "value": value, "weight": weight})

    def remove_asset(self, name: str) -> None:
        """Remove an asset by name."""
        original_len = len(self._assets)
        self._assets = [a for a in self._assets if a["name"] != name]
        if len(self._assets) == original_len:
            raise ValueError(f"Asset '{name}' not found in portfolio.")

    def total_value(self) -> float:
        """Return the sum of all asset values."""
        return round(sum(a["value"] for a in self._assets), 2)

    def weighted_return(self, returns: dict) -> float:
        """Calculate portfolio weighted return given a dict of {name: return}."""
        if not self._assets:
            raise ValueError("Portfolio is empty.")
        total = 0.0
        for asset in self._assets:
            name = asset["name"]
            if name not in returns:
                raise ValueError(f"Return for asset '{name}' not provided.")
            total += asset["weight"] * returns[name]
        return round(total, 2)

    def diversification_index(self) -> float:
        """Calculate inverted Herfindahl-Hirschman Index (1 = fully diversified)."""
        if not self._assets:
            raise ValueError("Portfolio is empty.")
        hhi = sum(a["weight"] ** 2 for a in self._assets)
        n = len(self._assets)
        if n == 1:
            return round(1 - hhi, 2)
        # Normalize: (1/n is min HHI for equal weights, 1 is max)
        min_hhi = 1.0 / n
        if hhi == min_hhi:
            return 1.0
        normalized = (1 - hhi) / (1 - min_hhi)
        return round(normalized, 4)

    def rebalance(self, target_weights: dict) -> dict:
        """Calculate adjustments needed to reach target weights."""
        if not self._assets:
            raise ValueError("Portfolio is empty.")
        total = self.total_value()
        if total == 0:
            raise ValueError("Total portfolio value is zero.")
        adjustments = {}
        for asset in self._assets:
            name = asset["name"]
            if name not in target_weights:
                raise ValueError(f"Target weight for asset '{name}' not provided.")
            target_value = total * target_weights[name]
            delta = round(target_value - asset["value"], 2)
            adjustments[name] = delta
        return adjustments

    def risk_exposure(self, volatilities: dict) -> float:
        """Calculate weighted risk exposure given {name: volatility}."""
        if not self._assets:
            raise ValueError("Portfolio is empty.")
        exposure = 0.0
        for asset in self._assets:
            name = asset["name"]
            if name not in volatilities:
                raise ValueError(f"Volatility for asset '{name}' not provided.")
            exposure += asset["weight"] * volatilities[name]
        return round(exposure, 4)

    def to_dict(self) -> dict:
        """Serialize portfolio to dictionary."""
        return {
            "assets": list(self._assets),
            "total_value": self.total_value(),
            "asset_count": len(self._assets),
        }

    def summary(self) -> str:
        """Return a formatted summary of the portfolio."""
        if not self._assets:
            return "Portfolio is empty."
        lines = [
            f"Portfolio Summary ({len(self._assets)} assets)",
            f"Total Value: R$ {self.total_value():,.2f}",
            "-" * 40,
        ]
        for asset in self._assets:
            lines.append(
                f"  {asset['name']:15s}  "
                f"R$ {asset['value']:>12,.2f}  "
                f"({asset['weight']*100:.1f}%)"
            )
        return "\n".join(lines)
