# gbp_leff_fixado.py
import numpy as np

# ----- CONSTANTES FIXAS -----
FORCE_TON = 160
LENGTH = 2.4
WIDTH = 1.8
THICKNESS = 0.30
YOUNG_GPA = 22
KS_KN_M3 = 50_000
PATCH_WIDTH = None     # None = carga pontual
NODES = 801

TON_TO_N = 9806.65
KGFCM2_TO_PA = 98066.5


def inertia_rectangular(b: float, h: float) -> float:
    return b * h**3 / 12.0


def winkler_leff(
    force_ton, length, width, thickness, young_gpa,
    ks_kn_m3, p_lim_abs_pa, patch_width, nodes
) -> dict[str, float]:
    force = force_ton * TON_TO_N
    young = young_gpa * 1e9
    ks = ks_kn_m3 * 1000
    i_sec = inertia_rectangular(width, thickness)
    dx = length / (nodes - 1)
    x = np.linspace(0.0, length, nodes)

    q = np.zeros_like(x)
    if patch_width is None:
        q[nodes // 2] = force / dx
    else:
        half = patch_width / 2.0
        mask = (x >= length / 2 - half) & (x <= length / 2 + half)
        q[mask] = force / (mask.sum() * dx)

    a = ks * dx**4 / (young * i_sec)
    rhs = q * dx**4 / (young * i_sec)
    mat = np.zeros((nodes, nodes))

    for i in range(2, nodes - 2):
        mat[i, i - 2] = 1.0
        mat[i, i - 1] = -4.0
        mat[i, i] = 6.0 + a
        mat[i, i + 1] = -4.0
        mat[i, i + 2] = 1.0

    mat[0, 0] = 1.0
    mat[1, 0], mat[1, 1] = -1.0 / dx, 1.0 / dx
    mat[-1, -1] = 1.0
    mat[-2, -2], mat[-2, -1] = -1.0 / dx, 1.0 / dx
    rhs[0] = rhs[1] = rhs[-1] = rhs[-2] = 0.0

    w = np.linalg.solve(mat, rhs)
    p = ks * w
    p_max = float(p.max())
    p_lim = p_lim_abs_pa

    i0 = int(np.argmax(p))
    i1, i2 = i0, i0
    while i1 > 0 and p[i1] >= p_lim:
        i1 -= 1
    while i2 < len(p) and p[i2] >= p_lim:
        i2 += 1

    leff_total = (i2 - i1 - 1) * dx
    return {
        "leff": leff_total / 2,
        "leff_total": leff_total,
        "p_max": p_max,
        "p_lim": p_lim,
    }


# ===== EXECUÇÃO VIA TERMINAL =====
if __name__ == "__main__":
    try:
        entrada = input("Resistência do solo (kgf/cm²): ").replace(",", ".")
        res_kgfcm2 = float(entrada)
    except ValueError:
        print("Entrada inválida.")
        exit(1)

    res_pa = res_kgfcm2 * KGFCM2_TO_PA

    out = winkler_leff(
        force_ton=FORCE_TON,
        length=LENGTH,
        width=WIDTH,
        thickness=THICKNESS,
        young_gpa=YOUNG_GPA,
        ks_kn_m3=KS_KN_M3,
        p_lim_abs_pa=res_pa,
        patch_width=PATCH_WIDTH,
        nodes=NODES,
    )

    print("\n──── Resultados ────")
    print(f"Resistência       : {res_kgfcm2:.2f} kgf/cm²")
    print(f"L_eff (um lado)   : {out['leff']:.3f} m")
    print(f"L_eff total       : {out['leff_total']:.3f} m")
    print(f"p_max             : {out['p_max'] / KGFCM2_TO_PA:.2f} kgf/cm²")
    print(f"p_lim aplicado    : {out['p_lim'] / KGFCM2_TO_PA:.2f} kgf/cm²")
