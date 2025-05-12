from nps_common import NPSCommon
from demographic_module import DemographicModule
from economic_module import EconomicModule
from finance_module import FinanceModule, SubscriberModule, BenefitModule
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
    def __init__(self):
        self.start_year = 2023  # 고정해야함 초기값등
        self.end_year = 2093

        self.common = NPSCommon()
        # 주요 모듈 초기화
        self.demographic = DemographicModule()  # 인구모듈
        self.economic = EconomicModule()  # 경제모듈
        self.subscriber = SubscriberModule(self.common)  # 가입자모듈
        self.benefit = BenefitModule(self.common)  # 급여모듈
        self.finance = FinanceModule(self.common)  # 재정모듈

    def run_projection(self):
        """재정추계 실행"""
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
                population_data["population_structure"],  # 인구구조 데이터 추가
                subscribers,
            )

            # 재정수지 추계
            financial_status = self.finance.project_balance(
                year, subscribers, benefits, economic_vars
            )
            # 연도별 계산결과 저장장
            results.append(financial_status)
        return {
            "financial_results": results,
            "demographic_results": demographic_results,
        }


if __name__ == "__main__":
    nps = NationalPensionModel()
    rs = nps.run_projection()

    save_results_to_csv(rs)
    create_financial_plots(rs)
    create_demographic_plots(rs)
