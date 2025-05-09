class InvestmentModule:
    def __init__(self, asset_allocation_scenario, expected_returns=None):
        self.asset_allocation = asset_allocation_scenario
        self.expected_returns = (
            expected_returns
            if expected_returns
            else self._get_default_expected_returns()
        )

    def _get_default_expected_returns(self):
        return {
            "domestic_stock": 0.06,  # 예시 값
            "foreign_stock": 0.07,  # 예시 값
            "domestic_bond": 0.03,  # 예시 값
            "foreign_bond": 0.04,  # 예시 값
            "alternative": 0.05,  # 예시 값
        }

    def calculate_portfolio_return(self):
        # 전체 포트폴리오의 기대 수익률 계산
        total_return = 0
        for asset, weight in self.asset_allocation.items():
            total_return += weight * self.expected_returns[asset]
        return total_return

    # TODO timedependent ALM strategy
    def update_asset_allocation(self, new_allocation):
        self.asset_allocation = new_allocation

    # TODO timedependent ALM strategy
    def update_expected_returns(self, new_returns):
        self.expected_returns.update(new_returns)


if __name__ == "__main__":
    # 2023년 9월 말 기준 포트폴리오 from보고서
    current_portfolio = {
        "domestic_stock": 0.140,
        "foreign_stock": 0.300,
        "domestic_bond": 0.319,
        "foreign_bond": 0.073,
        "alternative": 0.138,
    }

    # 사용자가 정의한 기대 수익률 (선택 사항)
    custom_returns = {
        "domestic_stock": 0.065,
        "foreign_stock": 0.075,
    }

    investment_mod = InvestmentModule(current_portfolio)  # 기본 기대 수익률 사용
    portfolio_return_default = investment_mod.calculate_portfolio_return()
    print(f"기본 기대 수익률 기반 포트폴리오 수익률: {portfolio_return_default:.4f}")

    investment_mod_custom = InvestmentModule(
        current_portfolio, custom_returns
    )  # 사용자 정의 기대 수익률 일부 사용
    investment_mod_custom.expected_returns  # 현재 적용된 기대 수익률 확인
    portfolio_return_custom = investment_mod_custom.calculate_portfolio_return()
    print(
        f"사용자 정의 기대 수익률 기반 포트폴리오 수익률: {portfolio_return_custom:.4f}"
    )

    # 다른 시나리오 (예: 주식 비중 확대)
    aggressive_portfolio = {
        "domestic_stock": 0.20,
        "foreign_stock": 0.40,
        "domestic_bond": 0.20,
        "foreign_bond": 0.05,
        "alternative": 0.15,
    }
    investment_mod.update_asset_allocation(aggressive_portfolio)
    portfolio_return_aggressive = investment_mod.calculate_portfolio_return()
    print(f"공격적 포트폴리오 수익률: {portfolio_return_aggressive:.4f}")
