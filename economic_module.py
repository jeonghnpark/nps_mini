import numpy as np
import pandas as pd


class EconomicModule:
    def __init__(self):
        """경제모듈 초기화"""
        self.params = {
            "gdp_growth_rate": {  # 실질 GDP 성장률
                2023: 0.019,
                2030: 0.019,
                2040: 0.013,
                2050: 0.007,
                2060: 0.004,
                2070: 0.002,
            },
            "wage_growth_rate": {  # 실질임금상승률
                2023: 0.019,
                2030: 0.019,
                2040: 0.019,
                2050: 0.018,
                2060: 0.017,
                2070: 0.016,
            },
            "inflation_rate": {  # 물가상승률 (보고서 p.12 참조)
                2023: 0.022,
                2024: 0.022,
                2025: 0.022,
                2026: 0.022,
                2027: 0.022,
                2030: 0.022,
                2040: 0.020,
                2050: 0.020,
                2060: 0.020,
            },
            "nominal_wage_growth_rate": {  # 명목임금상승률
                2023: 0.047,  # 4.7%
                2030: 0.044,  # 4.4%
                2040: 0.042,  # 4.2%
                2050: 0.040,  # 4.0%
                2060: 0.039,  # 3.9%
            },
        }

        self.base_values = {
            "nominal_gdp": 2100e12,  # 2023년 명목 GDP (2100조원)
            "nominal_wage": 3.85e6,  # 2023년 월평균 임금 (385만원)
        }

    def project_variables(self, year):

        # 성장률 추계
        gdp_growth = self._get_gdp_growth_rate(year)
        real_wage_growth = self._get_wage_growth_rate(year)
        inflation = self._get_inflation_rate(year)
        nominal_wage_growth = self._get_nominal_wage_growth_rate(year)

        # GDP 추계 (실질, 명목)
        real_gdp = self._calculate_real_gdp(year)
        nominal_gdp = self._calculate_nominal_gdp(year)

        # 임금 추계 (실질, 명목)
        real_wage = self._calculate_real_wage(year)
        nominal_wage = self._calculate_nominal_wage(year)

        return {
            "year": year,
            "gdp_growth_rate": gdp_growth,
            "real_wage_growth_rate": real_wage_growth,
            "inflation_rate": inflation,
            "nominal_wage_growth_rate": nominal_wage_growth,
            "real_gdp": real_gdp,
            "nominal_gdp": nominal_gdp,
            "real_wage": real_wage,
            "nominal_wage": nominal_wage,
        }

    def _get_gdp_growth_rate(self, year):

        years = sorted(self.params["gdp_growth_rate"].keys())
        rates = [self.params["gdp_growth_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _get_wage_growth_rate(self, year):

        years = sorted(self.params["wage_growth_rate"].keys())
        rates = [self.params["wage_growth_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _get_inflation_rate(self, year):

        years = sorted(self.params["inflation_rate"].keys())
        rates = [self.params["inflation_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _get_nominal_wage_growth_rate(self, year):

        years = sorted(self.params["nominal_wage_growth_rate"].keys())
        rates = [self.params["nominal_wage_growth_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def _calculate_real_gdp(self, year):

        base_year = 2023
        real_gdp = self.base_values["nominal_gdp"]

        for y in range(base_year + 1, year + 1):
            growth_rate = self._get_gdp_growth_rate(y)
            real_gdp *= 1 + growth_rate

        return real_gdp

    def _calculate_nominal_gdp(self, year):

        real_gdp = self._calculate_real_gdp(year)
        base_year = 2023
        inflation_factor = 1.0

        for y in range(base_year + 1, year + 1):
            inflation_rate = self._get_inflation_rate(y)
            inflation_factor *= 1 + inflation_rate

        return real_gdp * inflation_factor

    def _calculate_real_wage(self, year):

        base_year = 2023
        real_wage = self.base_values["nominal_wage"]

        for y in range(base_year + 1, year + 1):
            growth_rate = self._get_wage_growth_rate(y)
            real_wage *= 1 + growth_rate

        return real_wage

    def _calculate_nominal_wage(self, year):

        base_year = 2023
        nominal_wage = self.base_values["nominal_wage"]

        for y in range(base_year + 1, year + 1):
            growth_rate = self._get_nominal_wage_growth_rate(y)
            nominal_wage *= 1 + growth_rate

        return nominal_wage
