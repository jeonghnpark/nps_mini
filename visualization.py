from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.font_manager as fm

# 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"  # 윈도우의 경우
# plt.rcParams['font.family'] = 'AppleGothic'  # macOS의 경우
plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지

now = datetime.now()
timestamp = now.strftime("%d%H%M")


def save_results_to_csv(rs):
    financial_df = pd.DataFrame(rs["financial_results"])
    demographic_df = pd.DataFrame(rs["demographic_results"])

    """결과 데이터프레임을 CSV 파일로 저장"""
    financial_df.to_csv(
        f"csv/financial_results_실질_{timestamp}.csv", encoding="utf-8-sig", index=False
    )
    demographic_df.to_csv(
        f"csv/demographic_results_실질_{timestamp}.csv",
        encoding="utf-8-sig",
        index=False,
    )


def create_financial_plots(rs):
    """재정추계 결과 시각화"""
    financial_df = pd.DataFrame(rs["financial_results"])

    # 1. 적립금 추이
    plt.figure(figsize=(10, 8))
    plt.plot(
        financial_df["year"],
        financial_df["nominal_reserve_fund"] / 100000000,
        marker="o",
    )
    plt.title("연도별 적립금 추이", fontsize=12)
    plt.xlim(2023, 2085)
    plt.xlabel("연도", fontsize=10)
    plt.xticks(range(2023, 2087, 2))
    plt.ylabel("적립금 (조원)", fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f"images/data/nps_reserve_fund_{timestamp}.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 2. 수입-지출 추이
    plt.figure(figsize=(10, 8))
    plt.plot(
        financial_df["year"],
        financial_df["nominal_revenue"] / 100000000,
        marker="o",
        label="총수입",
    )
    plt.plot(
        financial_df["year"],
        financial_df["nominal_expenditure"] / 100000000,
        marker="o",
        label="총지출",
    )
    plt.title("연도별 수입-지출 추이", fontsize=12)
    plt.xlim(2023, 2085)
    plt.xlabel("연도", fontsize=10)
    plt.xticks(range(2023, 2087, 2))
    plt.ylabel("금액 (조원)", fontsize=10)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f"images/data/nps_revenue_expenditure_{timestamp}.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    # 3. 수지차 추이
    plt.figure(figsize=(10, 8))
    plt.plot(
        financial_df["year"],
        financial_df["nominal_balance"] / 100000000,
        marker="o",
        color="green",
    )
    plt.title("연도별 수지차 추이", fontsize=12)
    plt.xlim(2023, 2085)
    plt.xlabel("연도", fontsize=10)
    plt.xticks(range(2023, 2087, 2))
    plt.ylabel("금액 (조원)", fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f"images/data/nps_balance_{timestamp}.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 4. 적립률 추이
    plt.figure(figsize=(10, 8))
    plt.plot(
        financial_df["year"], financial_df["fund_ratio"], marker="o", color="purple"
    )
    plt.title("연도별 적립률 추이", fontsize=12)
    plt.xlim(2023, 2085)
    plt.xlabel("연도", fontsize=10)
    plt.xticks(range(2023, 2087, 2))
    plt.ylabel("적립률 (%)", fontsize=10)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f"images/data/nps_fund_ratio_{timestamp}.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 5. gdp대비 급여지출 추이
    plt.figure(figsize=(10, 8))
    plt.plot(
        financial_df["year"],
        financial_df["real_expenditure"] * 10000 / financial_df["real_gdp"] * 100,
        marker="o",
        color="orange",
    )
    plt.title("GDP 대비 급여지출 추이", fontsize=12)
    plt.xlim(2023, 2085)
    plt.xticks(range(2023, 2087, 2))
    plt.xlabel("연도", fontsize=10)
    plt.ylabel("GDP 대비 비중 (%)", fontsize=10)
    plt.grid(True)
    plt.savefig(
        f"images/data/nps_gdp_expenditure_{timestamp}.png", dpi=300, bbox_inches="tight"
    )
    plt.close()


def create_demographic_plots(rs):
    """인구 관련 지표 시각화"""
    demographic_df = pd.DataFrame(rs["demographic_results"])
    # 인구 관련 지표 4개 그래프를 2x2로 배치
    fig, axes = plt.subplots(1, 2, figsize=(16, 10))

    # 1. 인구 구조 추이 (좌상단)
    axes[0].plot(
        demographic_df["year"],
        demographic_df["total_population"] / 10000,
        marker="o",
        label="총인구",
    )
    axes[0].plot(
        demographic_df["year"],
        demographic_df["working_age_population"] / 10000,
        marker="o",
        label="생산가능인구",
    )
    axes[0].plot(
        demographic_df["year"],
        demographic_df["elderly_population"] / 10000,
        marker="o",
        label="노인인구",
    )
    axes[0].set_title("연도별 인구구조 추이", fontsize=12)
    axes[0].set_xlim(2023, 2085)
    axes[0].set_xlabel("연도", fontsize=10)
    axes[0].set_ylabel("인구 (만명)", fontsize=10)
    axes[0].legend()
    axes[0].grid(True)

    # 2. 노년부양비 추이 (우상단)
    axes[1].plot(
        demographic_df["year"],
        demographic_df["elderly_dependency"],
        marker="o",
        color="red",
    )
    axes[1].set_title("연도별 노년부양비 추이", fontsize=12)
    axes[1].set_xlim(2023, 2085)
    axes[1].set_xlabel("연도", fontsize=10)
    axes[1].set_ylabel("노년부양비 (%)", fontsize=10)
    axes[1].grid(True)

    plt.tight_layout()
    plt.savefig(
        f"images/data/nps_demographic_indicators_{timestamp}.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()


import numpy as np
import seaborn as sns


def create_simulation_visualizations(df):
    # 1. 히트맵: 보험료율과 소득대체율에 따른 최대적립금
    plt.figure(figsize=(12, 8))
    pivot_max_reserve = df.pivot(
        index="contribution_rate", columns="income_replacement", values="max_reserve"
    )
    sns.heatmap(pivot_max_reserve, cmap="YlOrRd", annot=True, fmt=".0f")
    plt.title("Maximum Reserve Fund by Contribution Rate and Income Replacement Rate")
    plt.xlabel("Income Replacement Rate (%)")
    plt.ylabel("Contribution Rate (%)")
    plt.tight_layout()
    plt.savefig("images/data/heatmap_max_reserve.png")
    plt.close()

    # 2. 라인 플롯: 보험료율별 기금소진연도
    plt.figure(figsize=(12, 6))
    for rate in df["contribution_rate"].unique():
        data = df[df["contribution_rate"] == rate]
        plt.plot(
            data["income_replacement"],
            data["depletion_year"],
            label=f"Contribution {rate}%",
            marker="o",
        )
    plt.title("Depletion Year by Income Replacement Rate")
    plt.xlabel("Income Replacement Rate (%)")
    plt.ylabel("Depletion Year")
    plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("images/data/lineplot_depletion.png")
    plt.close()

    # 2. 라인 플롯: 보험료율 vs 기금적자연도, 기금소진연도
    plt.figure(figsize=(12, 6))
    data = df[df["income_replacement"] == 40]
    plt.plot(
        data["contribution_rate"],
        data["first_deficit_year"],
        label=f"첫 적자 연도 - 소득대체율 {40}%",
        marker="o",
    )
    plt.plot(
        data["contribution_rate"],
        data["depletion_year"],
        label=f"기금 소진 연도 - 소득대체율 {40}%",
        marker="x",
    )
    plt.title("보험료율에 따른 적자 전환 및 기금 소진 연도")
    plt.xlabel("보험료율 (%)")
    plt.ylabel("연도")
    plt.yticks(
        np.arange(
            min(data["first_deficit_year"].min(), data["depletion_year"].min()),
            max(data["first_deficit_year"].max(), data["depletion_year"].max()) + 1,
            5,
        )
    )
    plt.legend(loc="best")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("images/data/lineplot_deficit_depletion_by_contribution.png")
    plt.close()

    # 2. 라인 플롯: 소득대체율 vs 기금적자연도, 기금 소진연도
    plt.figure(figsize=(12, 6))
    data = df[df["contribution_rate"] == 9]
    plt.plot(
        data["income_replacement"],
        data["first_deficit_year"],
        label=f"첫 적자 연도 - 보험료율 {9}%",
        marker="o",
    )
    plt.plot(
        data["income_replacement"],
        data["depletion_year"],
        label=f"기금 소진 연도 - 보험료율 {9}%",
        marker="x",
    )
    plt.title("소득대체율에 따른 적자 전환 및 기금 소진 연도")
    plt.xlabel("소득대체율 (%)")
    plt.ylabel("연도")
    plt.yticks(
        np.arange(
            min(data["first_deficit_year"].min(), data["depletion_year"].min()),
            max(data["first_deficit_year"].max(), data["depletion_year"].max()) + 1,
            2,
        )
    )
    plt.legend(loc="best")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("images/data/lineplot_deficit_depletion_by_income_replacement.png")
    plt.close()

    # 3. 3D 서피스 플롯: 최대적립금
    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")
    X = df["contribution_rate"].unique()
    Y = df["income_replacement"].unique()
    X, Y = np.meshgrid(X, Y)
    Z = df.pivot(
        index="income_replacement", columns="contribution_rate", values="max_reserve"
    ).values
    surf = ax.plot_surface(X, Y, Z, cmap="viridis")
    plt.colorbar(surf)
    ax.set_xlabel("Contribution Rate (%)")
    ax.set_ylabel("Income Replacement Rate (%)")
    ax.set_zlabel("Maximum Reserve (trillion won)")
    plt.title("Maximum Reserve Fund - 3D View")
    plt.tight_layout()
    plt.savefig("images/data/3d_surface_max_reserve.png")
    plt.close()

    # 4. 산점도: 최대적립금과 기금소진연도의 관계
    plt.figure(figsize=(10, 6))
    scatter = plt.scatter(
        df["max_reserve"],
        df["depletion_year"],
        c=df["contribution_rate"],
        cmap="viridis",
    )
    plt.colorbar(scatter, label="Contribution Rate (%)")
    plt.title("Maximum Reserve vs Depletion Year")
    plt.xlabel("Maximum Reserve (trillion won)")
    plt.ylabel("Depletion Year")
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("images/data/scatter_reserve_depletion.png")
    plt.close()


def save_stochastic_result_to_csv(rs, timestamp=None):
    """확률적 시뮬레이션 결과를 CSV 파일로 저장"""
    if timestamp is None:
        timestamp = now.strftime("%d%H%M")

    # 인구 데이터 저장 (시뮬레이션에서 공통)
    demographic_df = pd.DataFrame(rs["demographic_results"])
    demographic_df.to_csv(
        f"csv/demographic_results_stochastic_{timestamp}.csv",
        encoding="utf-8-sig",
        index=False,
    )

    # 연도별 통계 데이터 준비
    years = sorted(
        set([result["year"] for sim in rs["financial_results"] for result in sim])
    )
    stats_data = {
        "year": years,
        "mean_reserve": [],
        "median_reserve": [],
        "p5_reserve": [],
        "p95_reserve": [],
        "mean_balance": [],
        "median_balance": [],
        "p5_balance": [],
        "p95_balance": [],
    }

    # 연도별 결과 분석
    for year in years:
        # 해당 연도의 모든 시뮬레이션 결과 수집
        year_reserves = []
        year_balances = []

        for sim in rs["financial_results"]:
            for result in sim:
                if result["year"] == year:
                    year_reserves.append(result["nominal_reserve_fund"])
                    year_balances.append(result["nominal_balance"])
                    break

        # 통계 계산
        stats_data["mean_reserve"].append(np.mean(year_reserves))
        stats_data["median_reserve"].append(np.median(year_reserves))
        stats_data["p5_reserve"].append(np.percentile(year_reserves, 5))
        stats_data["p95_reserve"].append(np.percentile(year_reserves, 95))
        stats_data["mean_balance"].append(np.mean(year_balances))
        stats_data["median_balance"].append(np.median(year_balances))
        stats_data["p5_balance"].append(np.percentile(year_balances, 5))
        stats_data["p95_balance"].append(np.percentile(year_balances, 95))

    # 통계 데이터 저장
    stats_df = pd.DataFrame(stats_data)
    stats_df.to_csv(
        f"csv/stochastic_stats_{timestamp}.csv",
        encoding="utf-8-sig",
        index=False,
    )

    # 각 시뮬레이션별 소진 연도 계산
    depletion_years = []
    for sim_idx, sim in enumerate(rs["financial_results"]):
        depleted = False
        for i in range(len(sim) - 1):
            if (
                sim[i]["nominal_reserve_fund"] > 0
                and sim[i + 1]["nominal_reserve_fund"] <= 0
            ):
                depletion_years.append(
                    {"simulation": sim_idx, "depletion_year": sim[i + 1]["year"]}
                )
                depleted = True
                break

        if not depleted:
            # 소진되지 않은 경우
            depletion_years.append({"simulation": sim_idx, "depletion_year": None})

    depletion_df = pd.DataFrame(depletion_years)
    depletion_df.to_csv(
        f"csv/stochastic_depletion_years_{timestamp}.csv",
        encoding="utf-8-sig",
        index=False,
    )

    # 모든 시뮬레이션 결과를 저장
    all_results = []
    for sim_idx, sim in enumerate(rs["financial_results"]):
        for result in sim:
            result_copy = result.copy()
            result_copy["simulation"] = sim_idx
            all_results.append(result_copy)

    all_results_df = pd.DataFrame(all_results)
    all_results_df.to_csv(
        f"csv/stochastic_all_results_{timestamp}.csv",
        encoding="utf-8-sig",
        index=False,
    )

    print(f"확률적 시뮬레이션 결과가 csv 폴더에 저장되었습니다 ({timestamp})")


def create_stochastic_financial_plots(rs, timestamp=None, title="2022년말 비중"):
    """확률적 시뮬레이션 결과 시각화"""
    if timestamp is None:
        timestamp = now.strftime("%d%H%M")

    # 연도별 데이터 추출
    years = sorted(
        set([result["year"] for sim in rs["financial_results"] for result in sim])
    )

    # 적립금 데이터
    reserve_data = {year: [] for year in years}
    balance_data = {year: [] for year in years}

    for sim in rs["financial_results"]:
        for result in sim:
            year = result["year"]
            reserve_data[year].append(result["nominal_reserve_fund"])
            balance_data[year].append(result["nominal_balance"])

    # 연도별 통계 계산
    mean_reserve = [np.mean(reserve_data[year]) for year in years]
    median_reserve = [np.median(reserve_data[year]) for year in years]
    p5_reserve = [np.percentile(reserve_data[year], 5) for year in years]
    p95_reserve = [np.percentile(reserve_data[year], 95) for year in years]

    # 하위 5% 값들의 평균 계산
    bottom_5_percent_means = []
    for year in years:
        values = reserve_data[year]
        p5_threshold = np.percentile(values, 5)
        bottom_5_percent_values = [v for v in values if v <= p5_threshold]
        if bottom_5_percent_values:
            bottom_5_percent_means.append(np.mean(bottom_5_percent_values))
        else:
            bottom_5_percent_means.append(p5_threshold)  # 값이 없으면 5% 임계값 사용

    mean_balance = [np.mean(balance_data[year]) for year in years]
    median_balance = [np.median(balance_data[year]) for year in years]
    p5_balance = [np.percentile(balance_data[year], 5) for year in years]
    p95_balance = [np.percentile(balance_data[year], 95) for year in years]

    # 1. 적립금 추이 확률적 시각화
    plt.figure(figsize=(12, 8))

    # 신뢰 구간 (90%)
    plt.fill_between(
        years,
        [p / 100000000 for p in p5_reserve],
        [p / 100000000 for p in p95_reserve],
        alpha=0.3,
        color="blue",
        label="90% 신뢰구간",
    )

    # 평균값
    plt.plot(
        years,
        [m / 100000000 for m in mean_reserve],
        marker="o",
        color="blue",
        label="평균 적립금",
    )

    # 중앙값
    plt.plot(
        years,
        [m / 100000000 for m in median_reserve],
        linestyle="--",
        color="darkblue",
        label="중앙값 적립금",
    )
    # 하위 5% 평균값
    plt.plot(
        years,
        [m / 100000000 for m in bottom_5_percent_means],
        linestyle="-.",
        linewidth=2,
        color="black",
        label="하위 5% 평균 적립금",
    )
    plt.title("확률적 시뮬레이션: 연도별 적립금 추이", fontsize=14)
    plt.xlim(min(years), max(years))
    plt.xlabel("연도", fontsize=12)
    plt.ylabel("적립금 (조원)", fontsize=12)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f"images/data/stochastic_reserve_fund_{timestamp}.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    # 2. 수지차 추이 확률적 시각화
    plt.figure(figsize=(12, 8))

    # 신뢰 구간 (90%)
    plt.fill_between(
        years,
        [p / 100000000 for p in p5_balance],
        [p / 100000000 for p in p95_balance],
        alpha=0.3,
        color="green",
        label="90% 신뢰구간",
    )

    # 평균값
    plt.plot(
        years,
        [m / 100000000 for m in mean_balance],
        marker="o",
        color="green",
        label="평균 수지차",
    )

    # 중앙값
    plt.plot(
        years,
        [m / 100000000 for m in median_balance],
        linestyle="--",
        color="darkgreen",
        label="중앙값 수지차",
    )

    # 0선 (수지균형)
    plt.axhline(y=0, color="red", linestyle="-", alpha=0.7)

    plt.title("확률적 시뮬레이션: 연도별 수지차 추이", fontsize=14)
    plt.xlim(min(years), max(years))
    plt.xlabel("연도", fontsize=12)
    plt.ylabel("수지차 (조원)", fontsize=12)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f"images/data/stochastic_balance_{timestamp}.png", dpi=300, bbox_inches="tight"
    )
    plt.close()

    # 3. 시뮬레이션별 적립금 소진 연도 분포
    depletion_years = []

    for sim_idx, sim in enumerate(rs["financial_results"]):
        depleted = False
        for i in range(len(sim) - 1):
            if (
                sim[i]["nominal_reserve_fund"] > 0
                and sim[i + 1]["nominal_reserve_fund"] <= 0
            ):
                depletion_years.append(sim[i + 1]["year"])
                depleted = True
                break

        if not depleted and sim[-1]["nominal_reserve_fund"] <= 0:
            # 마지막 연도에 소진된 경우
            depletion_years.append(sim[-1]["year"])

    if depletion_years:  # 적립금이 소진된 시뮬레이션이 있는 경우만 그래프 생성
        plt.figure(figsize=(12, 6))
        plt.hist(
            depletion_years,
            bins=range(min(depletion_years), max(depletion_years) + 2),
            alpha=0.7,
            color="orange",
            edgecolor="black",
        )
        plt.title("확률적 시뮬레이션: 적립금 소진 연도 분포", fontsize=14)
        plt.xlabel("소진 연도", fontsize=12)
        plt.ylabel("시뮬레이션 횟수", fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(
            f"images/data/stochastic_depletion_distribution_{timestamp}.png",
            dpi=300,
            bbox_inches="tight",
        )
        plt.close()

    # 4. 확률적 시뮬레이션 경로 (몇 개의 시뮬레이션만 선택)
    plt.figure(figsize=(12, 8))

    # 중앙값 경로
    plt.plot(
        years,
        [m / 100000000 for m in median_reserve],
        linewidth=3,
        color="blue",
        label="중앙값 적립금",
    )

    # 하위 5% 평균값
    plt.plot(
        years,
        [m / 100000000 for m in bottom_5_percent_means],
        linewidth=3,
        color="black",
        label="하위 5% 평균 적립금",
    )

    # 랜덤하게 n개 시뮬레이션 선택하여 표시
    import random

    selected_sims = random.sample(
        range(len(rs["financial_results"])), min(100, len(rs["financial_results"]))
    )

    colors = ["red", "blue", "green", "purple", "orange"]
    for i, sim_idx in enumerate(selected_sims):
        sim = rs["financial_results"][sim_idx]
        sim_years = [result["year"] for result in sim]
        sim_reserves = [result["nominal_reserve_fund"] / 100000000 for result in sim]

        plt.plot(
            sim_years,
            sim_reserves,
            alpha=0.6,
            linewidth=1.5,
            color="gray",
            label=f"시뮬레이션 #{sim_idx}",
        )

    plt.title(f"{title}", fontsize=14)
    plt.xlim(min(years), max(years))
    plt.xlabel("연도", fontsize=12)
    plt.ylabel("적립금 (조원)", fontsize=12)
    # plt.legend()
    plt.legend(["중앙값 적립금", "하위 5% 평균 적립금"])

    plt.grid(True)
    plt.tight_layout()
    plt.savefig(
        f"images/data/stochastic_simulation_paths_{timestamp}.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close()

    print(f"확률적 시뮬레이션 시각화가 images/data 폴더에 저장되었습니다 ({timestamp})")


def create_stochastic_demographic_plots(rs, timestamp=None):
    """확률적 시뮬레이션의 인구 지표 시각화 (결정론적 모델과 동일)"""
    create_demographic_plots(rs)  # 인구 데이터는 확률적/결정론적 동일


if __name__ == "__main__":
    df = pd.read_csv("csv/simulation_results_20250202_220713.csv")
    create_simulation_visualizations(df)
