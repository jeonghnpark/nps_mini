from nps_common import NPSCommon
from demographic_module import DemographicModule
from economic_module import EconomicModule
from finance_module import FinanceModule, SubscriberModule, BenefitModule
from investment_module import InvestmentModule
from visualization import (
    save_results_to_csv,
    create_financial_plots,
    create_demographic_plots,
)
from datetime import datetime
import pandas as pd

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import platform

system_name = platform.system()

if system_name == "Windows":
    plt.rc("font", family="Malgun Gothic")
elif system_name == "Darwin":  # Mac
    plt.rc("font", family="AppleGothic")
else:  # Linux
    plt.rc("font", family="NanumGothic")

# 마이너스 기호 깨짐 방지
plt.rc("axes", unicode_minus=False)


now = datetime.now()
timestamp = now.strftime("%d%H%M")


class NationalPensionModel:
    def __init__(self, investment_scenario=None, custom_expected_returns=None):
        self.start_year = 2023  # 고정해야함 초기값등
        self.end_year = 2093

        self.common = NPSCommon()
        self.demographic = DemographicModule()  # 인구모듈
        self.economic = EconomicModule()  # 경제모듈
        self.subscriber = SubscriberModule(self.common)  # 가입자모듈
        self.benefit = BenefitModule(self.common)  # 급여모듈
        self.finance = FinanceModule(self.common)  # 재정모듈

        if investment_scenario is None:
            # 기본 투자 시나리오 (예: 2023년 9월 말 기준)
            investment_scenario = {
                "domestic_stock": 0.140,
                "foreign_stock": 0.300,
                "domestic_bond": 0.319,
                "foreign_bond": 0.073,
                "alternative": 0.138,
            }
        self.investment = InvestmentModule(investment_scenario, custom_expected_returns)

    def run_projection(self):
        results = []
        demographic_results = []

        for year in range(
            self.start_year, self.end_year + 1
        ):  # 2023년부터 2093년까지 추계계
            # 인구 projection
            population_data = self.demographic.project_population(year)

            # 거시경제변수 projection
            economic_vars = self.economic.project_variables(year)

            # 투자변수 projection
            portfolio_return = self.investment.calculate_portfolio_return()

            # 가입자 projection
            subscribers = self.subscriber.project_subscribers(
                year, population_data["population_structure"]
            )

            # 인구지표와 가입자 정보를 통합
            demographic_data = population_data["indicators"].copy()
            demographic_data.update(
                {
                    "total_subscribers": subscribers["total_subscribers"],
                    "total_income_nominal": subscribers["total_income_nominal"],
                    "total_income_real": subscribers["total_income_real"],
                }
            )

            demographic_results.append(demographic_data)

            # 급여지출 projection
            benefits = self.benefit.project_benefits(
                year,
                population_data["population_structure"],
                subscribers,
            )

            # 재정수지 projection
            financial_status = self.finance.project_balance(
                year, subscribers, benefits, economic_vars, portfolio_return
            )

            results.append(financial_status)
        return {
            "financial_results": results,
            "demographic_results": demographic_results,
        }


if __name__ == "__main__":
    # 기본 투자 시나리오
    nps = NationalPensionModel()
    rs = nps.run_projection()

    save_results_to_csv(rs)
    create_financial_plots(rs)
    create_demographic_plots(rs)

    # 주식비중 확대 시나리오
    aggressive_portfolio_scenario = {
        "domestic_stock": 0.20,
        "foreign_stock": 0.40,
        "domestic_bond": 0.20,
        "foreign_bond": 0.05,
        "alternative": 0.15,
    }

    nps_aggressive = NationalPensionModel(
        investment_scenario=aggressive_portfolio_scenario
    )
    rs_aggressive = nps_aggressive.run_projection()

    save_results_to_csv(rs_aggressive)
    create_financial_plots(rs_aggressive)
    create_demographic_plots(rs_aggressive)
