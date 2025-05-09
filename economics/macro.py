import numpy as np
import matplotlib.pyplot as plt

# 한글 폰트 설정
plt.rcParams["font.family"] = "Malgun Gothic"  # 윈도우의 경우
# plt.rcParams['font.family'] = 'AppleGothic'  # macOS의 경우
plt.rcParams["axes.unicode_minus"] = False  # 마이너스 기호 깨짐 방지

# 예시 데이터
A = 1.5  # 기술수준
K = 100  # 자본(예: 기계설비 10억원)
L = 50  # 노동(예: 근로자 50명)
alpha = 0.3  # 자본소득분배율


def cobb_douglas(A, K, L, alpha):
    """
    A: 총요소생산성 (기술수준)
    K: 자본투입량
    L: 노동투입량
    alpha: 자본소득분배율 (0~1 사이)
    """
    return A * (K**alpha) * (L ** (1 - alpha))


# 다양한 자본-노동 조합에 따른 생산량 변화
def plot_production_surface():
    K_range = np.linspace(50, 150, 100)
    L_range = np.linspace(25, 75, 100)
    K_grid, L_grid = np.meshgrid(K_range, L_range)

    Y = A * (K_grid**alpha) * (L_grid ** (1 - alpha))

    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")
    surf = ax.plot_surface(K_grid, L_grid, Y)

    ax.set_xlabel("자본(K)")
    ax.set_ylabel("노동(L)")
    ax.set_zlabel("생산량(Y)")
    plt.title("콥-더글라스 생산함수")
    plt.show()


# 생산량 계산
output = cobb_douglas(A, K, L, alpha)
plot_production_surface()
