import numpy as np


class NPSCommon:
    def __init__(self):

        self.common_params = {
            "inflation_rate": {  # 물가상승률 보고서 p11
                2023: 0.022,
                2024: 0.022,
                2025: 0.022,
                2026: 0.022,
                2027: 0.022,
                2030: 0.022,
                2040: 0.020,
                2050: 0.020,
                2060: 0.020,
            }
        }

    def get_inflation_rate(self, year):
        # 실질 물가 상승률률
        years = sorted(self.common_params["inflation_rate"].keys())
        rates = [self.common_params["inflation_rate"][y] for y in years]

        if year >= years[-1]:
            return rates[-1]
        return np.interp(year, years, rates)

    def get_cumulative_inflation(self, base_year, target_year):

        cumulative = 1.0
        for year in range(base_year + 1, target_year + 1):
            inflation_rate = self.get_inflation_rate(year)
            cumulative *= 1 + inflation_rate
        return cumulative
