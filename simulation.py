from NPS_model import NationalPensionModel
from visualization import create_simulation_visualizations
import pandas as pd
import numpy as np
from datetime import datetime

now = datetime.now()
timestamp = now.strftime("%d%H%M")


def run_single_simulation(contribution_rate, income_replacement):

    # 모델 초기화
    model = NationalPensionModel()

    # 보험료율과 소득대체율 설정
    model.finance.params["contribution_rate"] = contribution_rate
    model.benefit.params["income_replacement"] = income_replacement

    # 시뮬레이션 실행
    results = []
    for year in range(model.start_year, model.end_year + 1):
        # 1. 인구추계
        population_data = model.demographic.project_population(year)

        # 2. 거시경제변수 추계
        economic_vars = model.economic.project_variables(year)

        # 3. 가입자 추계
        subscribers = model.subscriber.project_subscribers(
            year, population_data["population_structure"]
        )

        # 4. 급여지출 추계
        benefits = model.benefit.project_benefits(
            year,
            population_data["population_structure"],
            subscribers,
        )

        # 5. 재정수지 추계
        financial_status = model.finance.project_balance(
            year, subscribers, benefits, economic_vars
        )

        results.append(financial_status)

    # 결과 분석
    df = pd.DataFrame(results)

    # 최대 적립금 및 해당 연도 찾기
    max_reserve_idx = df["nominal_reserve_fund"].idxmax()
    max_reserve = df.loc[max_reserve_idx, "nominal_reserve_fund"] / 1e8  # 조원 단위
    max_reserve_year = df.loc[max_reserve_idx, "year"]

    # 최초 수지적자 연도 찾기
    deficit_mask = df["nominal_balance"] <= 0
    first_deficit_year = (
        df[deficit_mask]["year"].iloc[0] if deficit_mask.any() else None
    )

    # 기금 소진 연도 찾기
    depletion_mask = df["nominal_reserve_fund"] <= 0
    depletion_year = (
        df[depletion_mask]["year"].iloc[0] if depletion_mask.any() else None
    )

    return {
        "max_reserve": round(max_reserve, 1),  # 소수점 첫째자리까지 표시
        "max_reserve_year": int(max_reserve_year),
        "first_deficit_year": int(first_deficit_year) if first_deficit_year else None,
        "depletion_year": int(depletion_year) if depletion_year else None,
    }


def run_pension_simulation(contribution_rate, income_replacement, sensitivity=True):

    # 기본 시뮬레이션 실행
    base_result = run_single_simulation(contribution_rate, income_replacement)
    print(
        f"base result 보험률 {contribution_rate*100:.0f}% 소득대체율 {income_replacement*100:.0f}% {base_result}"
    )
    if not sensitivity:
        return base_result

    # 민감도 분석
    delta = 0.01  # 1% 변화

    # 보험료율 +1% 시뮬레이션
    cont_up_result = run_single_simulation(
        contribution_rate + delta, income_replacement
    )
    cont_down_result = run_single_simulation(
        contribution_rate - delta, income_replacement
    )
    print(
        f"보험료율 +1% 시뮬레이션 보험률 {(contribution_rate + delta)*100:.0f}% 소득대체율 {income_replacement*100:.0f}% {cont_up_result}"
    )
    # 소득대체율 +1% 시뮬레이션
    replace_up_result = run_single_simulation(
        contribution_rate, income_replacement + delta
    )
    replace_down_result = run_single_simulation(
        contribution_rate, income_replacement - delta
    )
    print(
        f"소득대체율 +1% 시뮬레이션 보험률 {contribution_rate*100:.0f}% 소득대체율 {(income_replacement + delta)*100:.0f}% {replace_up_result}"
    )

    # 민감도 계산
    sensitivity_results = {
        "contribution_elasticity": {
            "max_reserve": (
                cont_up_result["max_reserve"] - cont_down_result["max_reserve"]
            )
            / 2,
            "max_reserve_year": (
                cont_up_result["max_reserve_year"]
                - cont_down_result["max_reserve_year"]
            )
            / 2,
            "first_deficit_year": (
                (
                    cont_up_result["first_deficit_year"]
                    - cont_down_result["first_deficit_year"]
                )
                / 2
                if cont_down_result["first_deficit_year"]
                else None
            ),
            "depletion_year": (
                (cont_up_result["depletion_year"] - cont_down_result["depletion_year"])
                / 2
                if cont_down_result["depletion_year"]
                else None
            ),
        },
        "replacement_elasticity": {
            "max_reserve": (
                replace_up_result["max_reserve"] - replace_down_result["max_reserve"]
            )
            / 2,
            "max_reserve_year": (
                replace_up_result["max_reserve_year"]
                - replace_down_result["max_reserve_year"]
            )
            / 2,
            "first_deficit_year": (
                (
                    replace_up_result["first_deficit_year"]
                    - replace_down_result["first_deficit_year"]
                )
                / 2
                if replace_down_result["first_deficit_year"]
                else None
            ),
            "depletion_year": (
                (
                    replace_up_result["depletion_year"]
                    - replace_down_result["depletion_year"]
                )
                / 2
                if replace_down_result["depletion_year"]
                else None
            ),
        },
    }

    # 기본 결과에 민감도 분석 결과 추가
    base_result["sensitivity"] = sensitivity_results

    return base_result


# 사용 예시
def test_simulation():
    """시뮬레이션 테스트 함수"""
    # 현행 제도 (보험료율 9%, 소득대체율 40%)
    result_current = run_pension_simulation(0.09, 0.40)
    print("\n현행 제도 시뮬레이션 결과:")
    print(
        f"최대 적립금: {result_current['max_reserve']}조원 ({result_current['max_reserve_year']}년)"
    )
    print(f"최초 수지적자 발생: {result_current['first_deficit_year']}년")
    print(f"기금 소진: {result_current['depletion_year']}년")

    # 보험료율 인상 시나리오 (보험료율 12%, 소득대체율 40%)
    result_higher_contribution = run_pension_simulation(0.12, 0.40)
    print("\n보험료율 인상 시나리오 결과:")
    print(
        f"최대 적립금: {result_higher_contribution['max_reserve']}조원 ({result_higher_contribution['max_reserve_year']}년)"
    )
    print(f"최초 수지적자 발생: {result_higher_contribution['first_deficit_year']}년")
    print(f"기금 소진: {result_higher_contribution['depletion_year']}년")


def run_multiple_simulations():

    # 시뮬레이션할 보험료율과 소득대체율 조합
    contribution_rates = [
        round(x, 2) for x in np.arange(0.07, 0.16, 0.01)
    ]  # 0.07부터 0.01씩 증가하여 0.15까지
    income_replacements = [
        round(x, 2) for x in np.arange(0.40, 0.51, 0.01)
    ]  # 40%부터 0.01씩 증가하여 50%까지

    results = []

    for cont_rate in contribution_rates:
        for inc_replace in income_replacements:
            # 시뮬레이션 실행
            print(
                f"Running simulation for contribution rate: {cont_rate * 100:.0f}%, income replacement: {inc_replace * 100:.0f}%"
            )

            result = run_pension_simulation(cont_rate, inc_replace, sensitivity=False)
            # 결과 저장
            results.append(
                {
                    "contribution_rate": cont_rate * 100,  # 퍼센트로 변환
                    "income_replacement": inc_replace * 100,  # 퍼센트로 변환
                    "max_reserve": result["max_reserve"],
                    "max_reserve_year": result["max_reserve_year"],
                    "first_deficit_year": result["first_deficit_year"],
                    "depletion_year": result["depletion_year"],
                }
            )

    # DataFrame 생성
    df_results = pd.DataFrame(results)

    # 결과 출력
    print("\n연금 재정 시뮬레이션 결과:")
    print("=" * 80)
    for _, row in df_results.iterrows():
        print(
            f"\n보험료율 {row['contribution_rate']}%, 소득대체율 {row['income_replacement']}% 시나리오:"
        )
        print(f"  최대 적립금: {row['max_reserve']}조원 ({row['max_reserve_year']}년)")
        print(f"  최초 수지적자 발생: {row['first_deficit_year']}년")
        print(f"  기금 소진: {row['depletion_year']}년")

    # CSV 파일로 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"csv/simulation_results_{timestamp}.csv"
    df_results.to_csv(csv_filename, index=False)

    return df_results


if __name__ == "__main__":
    df_result = run_multiple_simulations()
    create_simulation_visualizations(df_result)
