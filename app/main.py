from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import matplotlib.pyplot as plt
import io
import base64
from pathlib import Path

from NPS_model import NationalPensionModel

app = FastAPI()


app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/calculate")
async def calculate(
    contribution_rate: float = Form(...), income_replacement: float = Form(...)
):
    try:
        model = NationalPensionModel()
        model.finance.params["contribution_rate"] = (
            contribution_rate / 100
        )  # 퍼센트를 비율로 변환
        model.benefit.params["income_replacement"] = income_replacement / 100
        results = model.run_projection()
        financial_results = results["financial_results"]

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 12))

        years = [r["year"] for r in financial_results]
        reserve_funds = [
            r["nominal_reserve_fund"] / 100000000 for r in financial_results
        ]  # 조원 단위로 변환

        # 최대 적립금 시점 찾기
        max_reserve_idx = reserve_funds.index(max(reserve_funds))
        max_reserve_year = years[max_reserve_idx]
        max_reserve = reserve_funds[max_reserve_idx]

        # 적자전환 시점 찾기 (전년대비 감소 시작점)
        try:
            deficit_idx = next(
                i
                for i in range(1, len(reserve_funds))
                if reserve_funds[i] < reserve_funds[i - 1]
            )
            deficit_year = years[deficit_idx]
        except StopIteration:
            # 적자전환이 발생하지 않는 경우
            deficit_idx = None
            deficit_year = None

        # 기금 고갈 시점 찾기
        try:
            depletion_idx = next(i for i, x in enumerate(reserve_funds) if x <= 0)
            depletion_year = years[depletion_idx]
        except StopIteration:
            # 고갈시점이 없는 경우
            depletion_idx = None
            depletion_year = None

        # 첫 번째 그래프 (적립금 추이)
        ax1.plot(years, reserve_funds, marker="o")

        # 최대 적립금 표시
        ax1.annotate(
            f"최대 적립금\n{max_reserve_year}년\n{max_reserve:.1f}조원",
            xy=(max_reserve_year, max_reserve),
            xytext=(10, 30),
            textcoords="offset points",
            ha="left",
            va="bottom",
            bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.5),
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
        )

        # 적자전환 시점 표시
        if deficit_year is not None and deficit_idx is not None:
            ax1.annotate(
                f"적자전환\n{deficit_year}년",
                xy=(deficit_year, reserve_funds[deficit_idx]),
                xytext=(-10, -30),
                textcoords="offset points",
                ha="right",
                va="top",
                bbox=dict(boxstyle="round,pad=0.5", fc="orange", alpha=0.5),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            )

        # 기금 고갈 시점 표시
        if depletion_year is not None:
            ax1.annotate(
                f"기금고갈\n{depletion_year}년",
                xy=(depletion_year, 0),
                xytext=(10, -30),
                textcoords="offset points",
                ha="left",
                va="top",
                bbox=dict(boxstyle="round,pad=0.5", fc="red", alpha=0.5),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0"),
            )

        ax1.set_title("연도별 적립금 추이", loc="left")
        ax1.set_xlabel("연도")
        ax1.set_ylabel("적립금 (조원)")
        ax1.grid(True)

        # 두 번째 그래프 (수입-지출 추이)
        nominal_revenue = [r["nominal_revenue"] / 100000000 for r in financial_results]
        nominal_expenditure = [
            r["nominal_expenditure"] / 100000000 for r in financial_results
        ]

        ax2.plot(years, nominal_revenue, marker="o", label="총수입")
        ax2.plot(years, nominal_expenditure, marker="o", label="총지출")
        ax2.set_title("연도별 수입-지출 추이")
        ax2.set_xlabel("연도")
        ax2.set_ylabel("금액 (조원)")
        ax2.legend()
        ax2.grid(True)

        plt.tight_layout()

        # 이미지를 바이트로 변환
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format="png", bbox_inches="tight")
        plt.close()
        img_buf.seek(0)
        img_base64 = base64.b64encode(img_buf.getvalue()).decode()

        return JSONResponse(
            {
                "success": True,
                "image": img_base64,
                "max_reserve": max_reserve,
                "depletion_year": depletion_year,
                "deficit_year": deficit_year,
            }
        )

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})
