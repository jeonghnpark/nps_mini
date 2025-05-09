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


if __name__ == "__main__":
    df = pd.read_csv("csv/simulation_results_20250202_220713.csv")
    create_simulation_visualizations(df)
