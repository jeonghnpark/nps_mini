# 재정모듈
import pandas as pd
import numpy as np
from nps_common import NPSCommon


class FinanceModule:
    def __init__(self, common: NPSCommon):
        self.common = common
        self.params = {
            "contribution_rate": 0.09,
            "nominal_investment_return": {
                2023: 0.049,
                2030: 0.049,
                2040: 0.046,
                2050: 0.045,
                2060: 0.045,
            },
        }

        self.reserve_fund = 915e8  # 2023년 초기 명목 적립금 (915조원): 단위 만원
        self.real_reserve_fund = 915e8  # 2023년 초기 실질 적립금 (915조원): 단위 만원

    def project_balance(self, year, subscribers, benefits, economic_vars):

        # 실질 수입/지출/수지차 추계
        real_revenue = self._calculate_total_revenue(year, subscribers, economic_vars)
        real_expenditure = self._calculate_total_expenditure(year, benefits)
        real_balance = real_revenue - real_expenditure

        # 명목가치 변환
        cumulative_inflation = self._get_cumulative_inflation(2023, year)
        nominal_revenue = real_revenue * cumulative_inflation
        nominal_expenditure = real_expenditure * cumulative_inflation
        nominal_balance = real_balance * cumulative_inflation

        # 적립금 계산 (명목)
        self.reserve_fund = self._calculate_reserve_fund(year, nominal_balance)
        real_reserve_fund = self.reserve_fund / cumulative_inflation

        return {
            "year": year,
            "nominal_revenue": nominal_revenue,
            "real_revenue": real_revenue,
            "nominal_expenditure": nominal_expenditure,
            "real_expenditure": real_expenditure,
            "nominal_balance": nominal_balance,
            "real_balance": real_balance,
            "nominal_reserve_fund": self.reserve_fund,
            "real_reserve_fund": real_reserve_fund,
            "fund_ratio": self.reserve_fund / nominal_expenditure,
            "nominal_gdp": economic_vars["nominal_gdp"],
            "real_gdp": economic_vars["real_gdp"],
        }

    def _calculate_total_revenue(self, year, subscribers, economic_vars):
        # 보험료 수입 (실질가치)
        contribution_revenue = (
            subscribers["total_income_real"] * self.params["contribution_rate"]
        )
        # 투자 수익 (실질수익률 적용)
        real_return = self._get_real_investment_return(year)
        investment_revenue = self.reserve_fund * real_return

        return contribution_revenue + investment_revenue

    def _calculate_total_expenditure(self, year, benefits):
        # 1. 연금급여 지출 (실질가치)
        benefit_expenditure = benefits["total_benefits_real"]

        # 2. 관리운영비 (급여지출의 1% 가정)
        admin_cost = benefit_expenditure * 0.01

        return benefit_expenditure + admin_cost

    def _calculate_reserve_fund(self, year, balance):
        # 전년도 적립금 + 당해연도 수지
        new_reserve_fund = self.reserve_fund + balance

        # 적립금이 음수가 되는 경우 0으로 처리
        return max(0, new_reserve_fund)

    def _get_real_investment_return(self, year):
        nominal_return = self._get_nominal_investment_return(year)
        inflation_rate = self._get_inflation_rate(year)

        real_return = (1 + nominal_return) / (1 + inflation_rate) - 1
        return real_return

    def _get_nominal_investment_return(self, year):
        # 연도별 명목투자수익률
        years = sorted(self.params["nominal_investment_return"].keys())
        rates = [self.params["nominal_investment_return"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        else:
            return np.interp(year, years, rates)

    def _get_inflation_rate(self, year):
        return self.common.get_inflation_rate(year)

    def _get_cumulative_inflation(self, base_year, target_year):
        return self.common.get_cumulative_inflation(base_year, target_year)


class SubscriberModule:
    def __init__(self, common: NPSCommon):
        self.common = common
        self.params = {
            "participation_rate": {  # 가입률 -> 여성정책연구원 성인지 통계자료
                (18, 27): 0.31,  # 청년층
                (28, 49): 0.67,  # 핵심근로층
                (50, 59): 0.75,  # 준고령층
                (60, 64): 0.14,  # 고령층
            },
            "avg_income": {  # 연령대별 평균소득 (단위 월/만원)
                (18, 27): 250,  # 월 250만원
                (28, 49): 350,
                (50, 59): 380,
                (60, 64): 300,
            },
        }

    def _get_inflation_rate(self, year):
        return self.common.get_inflation_rate(year)

    def project_subscribers(self, year, population_structure):
        subscribers = {}
        total_income_real = 0

        # 물가상승률은 한 번만 계산
        cumulative_inflation = 1.0
        base_year = 2023
        for y in range(base_year + 1, year + 1):
            inflation_rate = self._get_inflation_rate(y)
            cumulative_inflation *= 1 + inflation_rate

        for age_group, rate in self.params["participation_rate"].items():
            # 해당 연령대 인구
            age_pop = population_structure[
                (population_structure["age"] >= age_group[0])
                & (population_structure["age"] <= age_group[1])
            ]["total"].sum()

            # 연령대 가입자 수
            subscribers[age_group] = age_pop * rate

            # 실질 소득 계산 (2023년 기준 실질가치)
            avg_income = self.params["avg_income"][age_group]
            total_income_real += subscribers[age_group] * avg_income * 12

        # 명목가치로 변환
        total_income_nominal = total_income_real * cumulative_inflation

        return {
            "year": year,
            "subscribers": subscribers,
            "total_subscribers": sum(subscribers.values()),
            "total_income_nominal": total_income_nominal,
            "total_income_real": total_income_real,
        }


class BenefitModule:
    def __init__(self, common: NPSCommon):
        self.common = common
        self.params = {
            "income_replacement": 0.40,  # 소득대체율 40%
            "avg_insured_period": {  # 평균가입기간
                2023: 15,
                2030: 18,
                2040: 22,
                2050: 25,
                2060: 28,
            },
            "benefit_rate": {  # 수급률 ( 인구 대비 65세 이상)
                2023: 0.440,  # 44.0%
                2030: 0.550,
                2040: 0.650,
                2050: 0.750,
                2060: 0.800,
            },
        }

    def _get_inflation_rate(self, year):  # subscriber와 중복됨 개선필요
        return self.common.get_inflation_rate(year)

    def _get_cumulative_inflation(self, base_year, target_year):
        return self.common.get_cumulative_inflation(base_year, target_year)

    def _get_benefit_rate(self, year):

        years = sorted(self.params["benefit_rate"].keys())
        rates = [self.params["benefit_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _get_avg_insured_period(self, year):

        years = sorted(self.params["avg_insured_period"].keys())
        periods = [self.params["avg_insured_period"][y] for y in years]

        if year >= years[-1]:
            return periods[-1]
        return np.interp(year, years, periods)

    def project_benefits(self, year, population_structure, subscribers_data):

        # 수급자 수 추계
        elderly_pop = population_structure[population_structure["age"] >= 65][
            "total"
        ].sum()
        benefit_rate = self._get_benefit_rate(year)
        beneficiaries = elderly_pop * benefit_rate

        # 평균급여액 계산 (실질가치 기준)
        avg_insured_period = self._get_avg_insured_period(year)
        avg_income_real = (
            subscribers_data["total_income_real"]
            / subscribers_data["total_subscribers"]
        )
        avg_benefit_real = (
            avg_income_real
            * self.params["income_replacement"]
            * (avg_insured_period / 40)
        )
        # 실질 총급여지출 계산
        total_benefits_real = beneficiaries * avg_benefit_real

        # 명목가치 변환
        cumulative_inflation = self._get_cumulative_inflation(2023, year)
        total_benefits_nominal = total_benefits_real * cumulative_inflation
        avg_benefit_nominal = avg_benefit_real * cumulative_inflation

        return {
            "year": year,
            "beneficiaries": beneficiaries,
            "avg_benefit_nominal": avg_benefit_nominal,
            "avg_benefit_real": avg_benefit_real,
            "total_benefits_nominal": total_benefits_nominal,
            "total_benefits_real": total_benefits_real,
        }
