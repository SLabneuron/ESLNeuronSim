import math

# ===== 数列を定義 =====
def a(k):
    # 好きに変えてよい
    # return 1 + 1/k
    # return 0 if k % 2 == 0 else 1
    return ((-1)**k) / k


# ===== パラメータ =====
N_max = 10      # n をどこまで見るか
K_max = 1000    # k をどこまで走らせるか（∞の代用）


# ===== 計算 =====
sup_tail = []
inf_tail = []

for n in range(1, N_max + 1):
    tail = [a(k) for k in range(n, K_max + 1)]

    sup_n = max(tail)
    inf_n = min(tail)

    sup_tail.append(sup_n)
    inf_tail.append(inf_n)

    print(f"n = {n:2d} | sup_{{k≥n}} a_k = {sup_n: .6f} | inf_{{k≥n}} a_k = {inf_n: .6f}")


# ===== limsup / liminf の近似 =====
limsup_approx = min(sup_tail)
liminf_approx = max(inf_tail)

print("\n--- 近似結果 ---")
print(f"limsup ≈ {limsup_approx: .6f}")
print(f"liminf ≈ {liminf_approx: .6f}")
