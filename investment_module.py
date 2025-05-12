import numpy as np
from nps_common import NPSCommon


class InvestmentModule:
    def __init__(
        self,
        common: NPSCommon,
        asset_allocation_scenario=None,
        expected_returns_scenario=None,
        volatilities_scenario=None,
        correlations_scenario=None,
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

        self.volatilities = (
            volatilities_scenario
            if volatilities_scenario
            else self._get_default_volatilities()
        )

        self.correlations = (
            correlations_scenario
            if correlations_scenario
            else self._get_default_correlations()
        )

    def _get_default_asset_allocation(self):

        # 표II-3
        asset_allocation_2022_end = {
            "domestic_stock": 0.141,
            "foreign_stock": 0.271,
            "domestic_bond": 0.349,
            "foreign_bond": 0.071,
            "alternative": 0.164,
        }

        # 표IV-5
        asset_allocation_2023_end = {
            "domestic_stock": 0.154,
            "foreign_stock": 0.33,
            "domestic_bond": 0.294,
            "foreign_bond": 0.08,
            "alternative": 0.142,
        }

        # 중기자산배분(가상)
        asset_allocation_midterm = {
            "domestic_stock": 0.124,
            "foreign_stock": 0.36,
            "domestic_bond": 0.294,
            "foreign_bond": 0.08,
            "alternative": 0.142,
        }

        return {
            "domestic_stock": 0.124,
            "foreign_stock": 0.36,
            "domestic_bond": 0.294,
            "foreign_bond": 0.08,
            "alternative": 0.142,
        }

    def _get_default_expected_returns(self):
        # 표V-2, '23~'30수익률
        return {
            "domestic_stock": 0.057,  # 국내 주식 명목 기대수익률 %
            "foreign_stock": 0.065,  # 해외 주식 명목 기대수익률 %
            "domestic_bond": 0.03,  # 국내 채권 명목 기대수익률 %
            "foreign_bond": 0.028,  # 해외 채권 명목 기대수익률 %
            "alternative": 0.057,  # 대체투자 명목 기대수익률 %
        }

    def _get_default_volatilities(self):
        #  표 Ⅴ-2(92페이지)에서 자산군별 변동성 정보
        return {
            "domestic_stock": 0.17,  # 국내주식 변동성(표준편차)
            "foreign_stock": 0.16,  # 해외주식 변동성
            "domestic_bond": 0.05,  # 국내채권 변동성
            "foreign_bond": 0.08,  # 해외채권 변동성
            "alternative": 0.10,  # 대체투자 변동성
        }

    def _get_default_correlations(self):

        # 상관관계 행렬 초기화 (단위 행렬)
        assets = list(self._get_default_asset_allocation().keys())
        n_assets = len(assets)

        corr_matrix = np.eye(n_assets)  # 이걸 리턴하면 상관계수= 0

        # 자산군 간 상관관계 설정 (예시 값, 실제 값으로 대체 필요)
        # corr_matrix[i, j] = corr_value  # i번째 자산과 j번째 자산의 상관관계

        # # 예시: 국내주식과 해외주식의 상관관계를 0.7로 설정
        # corr_matrix[0, 1] = corr_matrix[1, 0] = 0.7

        # # 예시: 주식과 채권의 상관관계를 -0.2로 설정
        # corr_matrix[0, 2] = corr_matrix[2, 0] = -0.2
        # corr_matrix[0, 3] = corr_matrix[3, 0] = -0.2
        # corr_matrix[1, 2] = corr_matrix[2, 1] = -0.2
        # corr_matrix[1, 3] = corr_matrix[3, 1] = -0.2

        # # 예시: 국내채권과 해외채권의 상관관계를 0.5로 설정
        # corr_matrix[2, 3] = corr_matrix[3, 2] = 0.5

        # # 예시: 대체투자와 다른 자산군의 상관관계 설정
        # corr_matrix[4, 0] = corr_matrix[0, 4] = 0.3  # 대체투자와 국내주식
        # corr_matrix[4, 1] = corr_matrix[1, 4] = 0.3  # 대체투자와 해외주식
        # corr_matrix[4, 2] = corr_matrix[2, 4] = 0.1  # 대체투자와 국내채권
        # corr_matrix[4, 3] = corr_matrix[3, 4] = 0.1  # 대체투자와 해외채권

        return {"matrix": corr_matrix, "assets": assets}

    # def update_asset_allocation(self, new_allocation):
    #     self.asset_allocation = new_allocation

    # def update_expected_returns(self, new_returns):
    #     self.expected_returns = new_returns

    # def calculate_nominal_portfolio_return(self, year=None):

    #     # TODO: 연도(year)별 자산배분
    #     total_return = 0
    #     total_weight = 0

    #     for asset, weight in self.asset_allocation.items():
    #         if asset in self.expected_returns:
    #             total_return += weight * self.expected_returns[asset]
    #             total_weight += weight
    #         else:
    #             print(f"Warning: Expected return for '{asset}' not found. Skipping.")

    #     return total_return

    # def calculate_real_portfolio_return(self, year):
    #     nominal_return = self.calculate_nominal_portfolio_return(year)
    #     inflation_rate = self.common.get_inflation_rate(year)

    #     # 명목 수익률을 실질 수익률로 변환: (1 + 명목수익률) / (1 + 물가상승률) - 1
    #     real_return = (1 + nominal_return) / (1 + inflation_rate) - 1
    #     return real_return

    def get_investment_returns(self, year=None):
        """
        deterministic assumption
        no vol and corr
        see simulation_return() for stochastic version.
        """
        # TODO: 연도(year)별 자산배분
        nominal_return = 0
        real_return = 0
        total_weight = 0

        # calculate nominl return
        for asset, weight in self.asset_allocation.items():
            if asset in self.expected_returns:
                nominal_return += weight * self.expected_returns[asset]
                total_weight += weight
            else:
                print(f"Warning: Expected return for '{asset}' not found. Skipping.")

        inflation_rate = self.common.get_inflation_rate(year)

        # convert nominal rtn to real rtn : (1 + nominal_return) / (1 + inflation-rate) - 1
        real_return = (1 + nominal_return) / (1 + inflation_rate) - 1

        return {"nominal": nominal_return, "real": real_return}

    def calculate_portfolio_volatility(self):

        assets = self.correlations["assets"]
        corr_matrix = self.correlations["matrix"]
        n_assets = len(assets)

        # 가중치 벡터 생성
        weights = np.zeros(n_assets)
        for i, asset in enumerate(assets):
            if asset in self.asset_allocation:
                weights[i] = self.asset_allocation[asset]

        # 변동성 벡터 생성
        vols = np.zeros(n_assets)
        for i, asset in enumerate(assets):
            if asset in self.volatilities:
                vols[i] = self.volatilities[asset]

        # 공분산 행렬 생성
        cov_matrix = np.zeros((n_assets, n_assets))
        for i in range(n_assets):
            for j in range(n_assets):
                cov_matrix[i, j] = corr_matrix[i, j] * vols[i] * vols[j]

        # 포트폴리오 변동성 계산
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)

        return portfolio_volatility
