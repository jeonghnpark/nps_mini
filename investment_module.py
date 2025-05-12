import numpy as np
from nps_common import NPSCommon


class InvestmentModule:
    def __init__(
        self,
        common: NPSCommon,
        asset_allocation_scenario=None,
        expected_returns_scenario=None,
    ):

        self.common = common
        self.asset_allocation = (
            asset_allocation_scenario
            if asset_allocation_scenario
            else self._get_default_asset_allocation()
        )
        self.expected_returns = (
            expected_returns_scenario
            if expected_returns_scenario
            else self._get_default_expected_returns()
        )

    def _get_default_asset_allocation(self):
        return {
            "domestic_stock": 0.15,
            "foreign_stock": 0.33,
            "domestic_bond": 0.30,
            "foreign_bond": 0.08,
            "alternative": 0.14,
        }

    def _get_default_expected_returns(self):

        return {
            "domestic_stock": 0.057,  # 국내 주식 명목 기대수익률 %
            "foreign_stock": 0.065,  # 해외 주식 명목 기대수익률 %
            "domestic_bond": 0.03,  # 국내 채권 명목 기대수익률 %
            "foreign_bond": 0.028,  # 해외 채권 명목 기대수익률 %
            "alternative": 0.057,  # 대체투자 명목 기대수익률 %
        }

    def update_asset_allocation(self, new_allocation):
        self.asset_allocation = new_allocation

    def update_expected_returns(self, new_returns):
        self.expected_returns = new_returns

    def calculate_nominal_portfolio_return(self, year=None):

        # TODO: 연도(year)별 자산배분
        total_return = 0
        total_weight = 0

        for asset, weight in self.asset_allocation.items():
            if asset in self.expected_returns:
                total_return += weight * self.expected_returns[asset]
                total_weight += weight
            else:
                print(f"Warning: Expected return for '{asset}' not found. Skipping.")

        return total_return

    def calculate_real_portfolio_return(self, year):
        nominal_return = self.calculate_nominal_portfolio_return(year)
        inflation_rate = self.common.get_inflation_rate(year)

        # 명목 수익률을 실질 수익률로 변환: (1 + 명목수익률) / (1 + 물가상승률) - 1
        real_return = (1 + nominal_return) / (1 + inflation_rate) - 1
        return real_return

    def get_investment_returns(self, year):
        nominal_return = self.calculate_nominal_portfolio_return(year)
        real_return = self.calculate_real_portfolio_return(year)
        return {"nominal": nominal_return, "real": real_return}
