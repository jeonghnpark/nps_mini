import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"  # 윈도우의 경우
# plt.rcParams['font.family'] = 'AppleGothic'  # macOS의 경우
plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지


class DemographicModule:
    def __init__(self):
        """인구모듈 초기화"""

        # self.population_structure = None  # 전체 인구
        # 보고서 참조
        self.population_structure = create_initial_population_2023()

        self.working_age = None  # 생산가능인구 (18-64세)
        self.elderly = None  # 고령인구 (65세 이상)

        self.params = {
            "fertility_rate": {  # 합계출산율 보고서 p11
                2023: 0.73,
                2030: 0.96,
                2040: 1.19,
                2050: 1.21,
                2060: 1.21,
                2070: 1.21,
            },
            "life_expectancy": {  # 기대수명 보고서 p11
                2023: 84.3,
                2030: 85.7,
                2040: 87.4,
                2050: 88.9,
                2060: 90.1,
                2070: 91.2,
            },
            "net_migration": {  # 국제순이동(천명) 보고서 p11
                2023: 43,
                2030: 46,
                2040: 46,
                2050: 43,
                2060: 43,
                2070: 40,
            },
        }

    def project_population(self, year):

        # 1. 연령별/성별 인구구조 계산
        population_structure = self._calculate_population_structure(year)

        # 2. 주요 인구지표 계산
        demographic_indicators = {
            "year": year,
            "total_population": population_structure["total"].sum(),
            "working_age_population": population_structure[
                (population_structure["age"] >= 18) & (population_structure["age"] < 65)
            ]["total"].sum(),
            "elderly_population": population_structure[
                population_structure["age"] >= 65
            ]["total"].sum(),
        }
        demographic_indicators["elderly_dependency"] = (
            demographic_indicators["elderly_population"]
            / demographic_indicators["working_age_population"]
            * 100
        )

        return {
            "population_structure": population_structure,
            "indicators": demographic_indicators,
        }

    def _calculate_population_structure(self, year):
        """연령별/성별 인구구조 계산 (간단한 코호트 요인법)

        TODO :  더 정교한 연령별/성별 사망률 적용
            연령별 출산율 차등 적용
            연령별/성별 국제순이동 패턴 반영
            코호트별 특성 반영
        """

        if year == 2023:  # 초기 인구구조조
            return self.population_structure

        prev_population_struct = self._calculate_population_structure(year - 1).copy()

        # 연령 증가 (모든 연령층을 1세 증가)
        prev_population_struct["age"] += 1

        # 사망률
        survival_rates = self._get_survival_rates(prev_population_struct["age"])
        prev_population_struct["male"] *= survival_rates
        prev_population_struct["female"] *= survival_rates

        # 출생아 수 계산
        fertility_rate = self.get_fertility_rate(year)
        fertile_women = prev_population_struct[
            (prev_population_struct["age"] >= 15)
            & (prev_population_struct["age"] <= 49)
        ]["female"].sum()

        total_births = (
            fertile_women * fertility_rate / (49 - 15 + 1)
        )  # 합계출산율->연간 출생아수로 전환

        # 출생성비 5:5로 그냥 적용
        male_births = total_births * 0.5
        female_births = total_births * 0.5

        # 4. 신생아 행 추가
        newborn_row = pd.DataFrame(
            {
                "age": [0],
                "total": [male_births + female_births],
                "male": [male_births],
                "female": [female_births],
            }
        )

        # 5. 국제순이동 반영 (간단히 전체 인구에 비례하여 배분)
        net_migration = self._get_net_migration(year)
        migration_ratio = net_migration / prev_population_struct["total"].sum()

        prev_population_struct["male"] *= 1 + migration_ratio
        prev_population_struct["female"] *= 1 + migration_ratio

        # 6. 최종 인구구조 생성
        population_structure = pd.concat(
            [newborn_row, prev_population_struct[prev_population_struct["age"] <= 200]]
        )
        population_structure["total"] = (
            population_structure["male"] + population_structure["female"]
        )

        return population_structure.reset_index(drop=True)

    def _get_survival_rates(self, ages):
        # 출처 ->통계청 사망원인통계
        survival_rates = np.ones(len(ages))

        survival_rates[ages == 0] = 0.995
        survival_rates[(ages >= 1) & (ages < 40)] = 0.999
        survival_rates[(ages >= 40) & (ages < 70)] = 0.995
        survival_rates[(ages >= 70) & (ages < 90)] = 0.98
        survival_rates[ages >= 90] = 0.90

        return survival_rates

    def _get_net_migration(self, year):
        years = sorted(self.params["net_migration"].keys())
        migration = [self.params["net_migration"][y] for y in years]
        return np.interp(year, years, migration) * 1000  # 천명 단위를 명 단위로 변환

    def get_fertility_rate(self, year):
        years = sorted(self.params["fertility_rate"].keys())
        rates = [self.params["fertility_rate"][y] for y in years]
        return np.interp(year, years, rates)


def create_initial_population_2023():
    """2023년 초기 인구구조 생성
    14페이지 참조
    """
    # 연령대별 인구 (만명)
    age_groups = {"under_18": 705, "18_64": 3501, "65_plus": 950}

    population_structure = []

    # 보고서의 인구 구성을 적당히 선형 보간함함
    young_total = age_groups["under_18"] * 10000  # 만명을 명으로 변환
    for age in range(18):
        weight = 0.8 + (age / 17) * 0.4  # 0세: 0.8, 17세: 1.2로 선형 증가
        pop_at_age = (
            young_total * weight / sum([0.8 + (a / 17) * 0.4 for a in range(18)])
        )
        population_structure.append(
            {
                "age": age,
                "total": pop_at_age,
                "male": pop_at_age * 0.5,
                "female": pop_at_age * 0.5,
            }
        )

    # 18-64세 인구 분포 (40-50대가 가장 많음)
    working_total = age_groups["18_64"] * 10000
    for age in range(18, 65):
        if 40 <= age <= 55:  # 40-55세는 더 높은 비중
            weight = 1.3
        else:
            weight = 0.8
        pop_at_age = (
            working_total * weight / (0.8 * 32 + 1.3 * 15)
        )  # 32년은 0.8비중, 15년은 1.3비중
        population_structure.append(
            {
                "age": age,
                "total": pop_at_age,
                "male": pop_at_age * 0.5,
                "female": pop_at_age * 0.5,
            }
        )

    # 65세 이상 인구 분포 (초기에 높고 점차 감소)
    elderly_total = age_groups["65_plus"] * 10000
    for age in range(65, 101):
        weight = (
            2.0 if age < 75 else (1.0 if age < 85 else 0.5)
        )  # 65-74세, 75-84세, 85세 이상 구분
        pop_at_age = (
            elderly_total * weight / (2.0 * 10 + 1.0 * 10 + 0.5 * 16)
        )  # 각 구간별 연수 고려
        population_structure.append(
            {
                "age": age,
                "total": pop_at_age,
                "male": pop_at_age * 0.5,
                "female": pop_at_age * 0.5,
            }
        )

    return pd.DataFrame(population_structure)


def save_pop_structure(df):
    # 인구구조 시각화
    plt.figure(figsize=(12, 6))

    # 남성 인구는 음수로 표시
    plt.barh(df["age"], -df["male"] / 10000, color="skyblue", alpha=0.7, label="남성")
    # 여성 인구는 양수로 표시
    plt.barh(df["age"], df["female"] / 10000, color="pink", alpha=0.7, label="여성")

    plt.title("2023년 인구피라미드", fontsize=14)
    plt.xlabel("인구 (만명)", fontsize=12)
    plt.ylabel("연령", fontsize=12)

    # x축 레이블을 절대값으로 표시
    xticks = plt.xticks()[0]
    plt.xticks(xticks, [abs(x) for x in xticks])

    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    # 이미지 저장
    plt.savefig("images/population_pyramid_2023.png", dpi=300, bbox_inches="tight")
    plt.close()


def test_demographic_module():
    demo = DemographicModule()
    demo.population_structure = create_initial_population_2023()
    # save_pop_structure(demo.population_structure)
    results_list = []
    for year in range(2023, 2094):
        result = demo.project_population(year)
        results_list.append(
            {
                "year": year,
                "total_population": result["indicators"]["total_population"],
                "working_age_population": result["indicators"][
                    "working_age_population"
                ],
                "elderly_population": result["indicators"]["elderly_population"],
                "elderly_dependency": result["indicators"]["elderly_dependency"],
                "population_structure": result["population_structure"],
            }
        )

    results_df = pd.DataFrame(results_list)
    print("\n인구추계 결과:")
    print(results_df)

    import matplotlib.pyplot as plt

    plt.figure(figsize=(12, 6))
    plt.plot(
        results_df["year"], results_df["total_population"] / 10000, "b-", linewidth=2
    )
    plt.title("total population(2023-2093)", fontsize=14)
    plt.xlabel("year", fontsize=12)
    plt.ylabel("total pupulation (10000 person)", fontsize=12)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    test_demographic_module()
