from nps_common import NPSCommon
from demographic_module import DemographicModule
from economic_module import EconomicModule
from finance_module import FinanceModule, SubscriberModule, BenefitModule
from investment_module import InvestmentModule
from visualization import (
    save_results_to_csv,
    create_financial_plots,
    create_demographic_plots,
    save_stochastic_result_to_csv,
    create_stochastic_financial_plots,
    create_stochastic_demographic_plots,
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
    def __init__(
        self,
        asset_allocation=None,
        expected_returns=None,
        stochastic=False,
        simulation_number=100,
    ):
        self.start_year = 2023  # 고정해야함 초기값등
        self.end_year = 2093

        self.common = NPSCommon()

        self.demographic = DemographicModule()  # 인구모듈
        self.economic = EconomicModule()  # 경제모듈
        self.subscriber = SubscriberModule(self.common)  # 가입자모듈
        self.benefit = BenefitModule(self.common)  # 급여모듈

        # InvestmentModule 초기화
        self.investment = InvestmentModule(
            self.common,
            asset_allocation_scenario=asset_allocation,
            expected_returns_scenario=expected_returns,
            stochastic=stochastic,
            simulation_number=simulation_number,
        )

        self.finance = FinanceModule(self.common, self.investment)

    def run_projection(self):
        if not self.investment.stochastic:
            # 기존 deterministic 방식
            self.finance = FinanceModule(self.common, self.investment)
            results = []
            demographic_results = []  # 인구지표 저장용

            for year in range(self.start_year, self.end_year + 1):
                # 인구추계
                population_data = self.demographic.project_population(year)

                # 거시경제변수 추계
                economic_vars = self.economic.project_variables(year)

                # 가입자 추계
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

                # 급여지출 추계
                benefits = self.benefit.project_benefits(
                    year,
                    population_data["population_structure"],
                    subscribers,
                )

                # 재정수지 추계
                financial_status = self.finance.project_balance(
                    year, subscribers, benefits, economic_vars
                )
                # 연도별 계산결과 저장
                results.append(financial_status)

            return {
                "financial_results": results,
                "demographic_results": demographic_results,
            }
        else:
            # 확률적 시뮬레이션 방식
            # 시뮬레이션 결과를 저장할 리스트
            stochastic_results = []
            demographic_results = []  # 인구지표는 한 번만 계산

            # 먼저 인구, 경제변수, 가입자 데이터 계산 (시뮬레이션에서 공통으로 사용)
            population_data_by_year = {}
            economic_vars_by_year = {}
            subscribers_by_year = {}
            benefits_by_year = {}

            # 공통 데이터 계산
            for year in range(self.start_year, self.end_year + 1):
                population_data = self.demographic.project_population(year)
                population_data_by_year[year] = population_data

                economic_vars = self.economic.project_variables(year)
                economic_vars_by_year[year] = economic_vars

                subscribers = self.subscriber.project_subscribers(
                    year, population_data["population_structure"]
                )
                subscribers_by_year[year] = subscribers

                benefits = self.benefit.project_benefits(
                    year, population_data["population_structure"], subscribers
                )
                benefits_by_year[year] = benefits

                # 인구지표 저장 (시뮬레이션간 공통)
                if len(demographic_results) < self.end_year - self.start_year + 1:
                    demographic_data = population_data["indicators"].copy()
                    demographic_data.update(
                        {
                            "year": year,
                            "total_subscribers": subscribers["total_subscribers"],
                            "total_income_nominal": subscribers["total_income_nominal"],
                            "total_income_real": subscribers["total_income_real"],
                        }
                    )
                    demographic_results.append(demographic_data)

            # 시뮬레이션 실행
            for sim_index in range(self.investment.simulation_number):
                # 시뮬레이션별 finance 모듈 초기화
                if sim_index % 100 == 0:
                    print(f"{sim_index+1}th simulations ")
                sim_finance = FinanceModule(self.common, self.investment)
                sim_results = []

                for year in range(self.start_year, self.end_year + 1):
                    # 저장된 데이터 사용
                    subscribers = subscribers_by_year[year]
                    benefits = benefits_by_year[year]
                    economic_vars = economic_vars_by_year[year]

                    # simulation_index를 전달하여 확률적 수익률 생성
                    self.investment.get_investment_returns(
                        year, simulation_index=sim_index
                    )

                    # 재정수지 추계
                    financial_status = sim_finance.project_balance(
                        year, subscribers, benefits, economic_vars
                    )

                    # 시뮬레이션 인덱스 추가
                    financial_status["simulation"] = sim_index
                    sim_results.append(financial_status)

                stochastic_results.append(sim_results)

            return {
                "financial_results": stochastic_results,
                "demographic_results": demographic_results,
            }


if __name__ == "__main__":

    title = "중기자산배분안(가정정)"
    # 결정론적 모델 실행
    nps = NationalPensionModel()
    rs = nps.run_projection()
    save_results_to_csv(rs, title=title)
    create_financial_plots(rs, title=title)
    create_demographic_plots(rs, title=title)

    # 확률적 모델 실행
    nps_stochastic = NationalPensionModel(stochastic=True, simulation_number=1000)
    rs_stochastic = nps_stochastic.run_projection()
    save_stochastic_result_to_csv(rs_stochastic, title=title)
    create_stochastic_financial_plots(rs_stochastic, timestamp=None, title=title)
    create_stochastic_demographic_plots(rs_stochastic, title=title)
