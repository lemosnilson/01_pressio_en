# -*- coding: utf-8 -*-
import math

"""
Script para análise de bases de grua (Crane Mats) usando 3 MÉTODOS
baseado no paper "Effective Bearing Length of Crane Mats" de David Duerr.

Versão com variáveis alinhadas à interface do app PRESSIO.
"""


# --- Função para Entrada de Dados ---
def obter_entrada_numerica(prompt):
    while True:
        entrada = input(prompt)
        try:
            valor = float(entrada.replace(',', '.'))
            return valor
        except ValueError:
            print("Erro: Por favor, insira um valor numérico válido.")


# --- MÉTODO 1: BASEADO NA CAPACIDADE DO SOLO ---
def calcular_metodo_capacidade_solo(p_newtons, w_newtons, qa_pascals, B, H, Fb_pascals, Fv_pascals, modulo_de_seccao):
    print("\n--- MÉTODO 1: Análise baseada na Capacidade do Solo ---")
    print("Objetivo: Dimensionar a base para que o solo não falhe, e verificar as tensões na base.")

    a_reqd = (p_newtons + w_newtons) / qa_pascals
    l_reqd = a_reqd / B if B > 0 else 0
    lc = l_reqd / 2.0
    q_p = p_newtons / (l_reqd * B) if (l_reqd * B) > 0 else 0
    m = (q_p * B) * (lc ** 2) / 2
    f_b_calc = m / modulo_de_seccao if modulo_de_seccao > 0 else 0
    v = (q_p * B) * (lc - H) if lc > H else 0
    f_v_calc = (1.5 * v) / (B * H) if (B * H) > 0 else 0

    print(f"Comprimento de apoio necessário (L_reqd): {l_reqd:.2f} m")
    print(f"Tensão de flexão resultante (fb): {f_b_calc / 1e6:.2f} MPa (Admissível: {Fb_pascals / 1e6:.2f} MPa)")
    print(f"Tensão de cisalhamento resultante (fv): {f_v_calc / 1e6:.2f} MPa (Admissível: {Fv_pascals / 1e6:.2f} MPa)")
    if f_b_calc <= Fb_pascals and f_v_calc <= Fv_pascals:
        print("Resultado: A base RESISTE às tensões para este comprimento.")
    else:
        print("Resultado: A base NÃO RESISTE às tensões para este comprimento.")


# --- MÉTODO 2: BASEADO NA RESISTÊNCIA DA BASE (VERSÃO COMPLETA) ---
def calcular_metodo_resistencia_base(p_newtons, w_newtons, qa_pascals, B, C, H, Fb_pascals, Fv_pascals,
                                     modulo_de_seccao):
    print("\n--- MÉTODO 2: Análise baseada na Resistência da Base (Flexão e Cisalhamento) ---")
    print("Objetivo: Encontrar o Leff limitante da base e verificar se o solo suporta.")

    m_max = Fb_pascals * modulo_de_seccao
    a_flex = p_newtons
    b_flex = -2 * p_newtons * C - 8 * m_max
    c_flex = p_newtons * C ** 2
    discriminante_flex = b_flex ** 2 - 4 * a_flex * c_flex
    leff_flexao = float('inf')
    if discriminante_flex >= 0:
        leff_flexao = (-b_flex + math.sqrt(discriminante_flex)) / (2 * a_flex)

    vn_max = (Fv_pascals * B * H) / 1.5
    leff_cisalhamento = float('inf')
    if p_newtons > 2 * vn_max:
        leff_cisalhamento = (p_newtons * (C + 2 * H)) / (p_newtons - 2 * vn_max)

    leff = min(leff_flexao, leff_cisalhamento)
    modo_de_falha = "Flexão" if leff == leff_flexao else "Cisalhamento"

    print(f"Leff limitado pela Flexão: {leff_flexao:.2f} m")
    print(f"Leff limitado pelo Cisalhamento: {leff_cisalhamento:.2f} m")
    print(f"Modo de falha governante da base: {modo_de_falha} em Leff = {leff:.2f} m")

    q_t = (p_newtons + w_newtons) / (leff * B) if leff * B > 0 else 0
    print(f"Pressão resultante no solo (qt): {q_t / 1e6:.4f} MPa (Admissível: {qa_pascals / 1e6:.4f} MPa)")

    if q_t <= qa_pascals:
        print("Resultado: O solo RESISTE à pressão para esta configuração.")
    else:
        print("Resultado: O solo NÃO RESISTE à pressão para esta configuração.")


# --- MÉTODO 3: CÁLCULO DO LEFF EFETIVO (PROPOSTA DO AUTOR) ---
def calcular_metodo_leff_efetivo(qa_pascals, w_newtons, L, B, H, C, Fb_pascals, Fv_pascals, E_pascals,
                                 modulo_de_seccao, momento_de_inercia):
    print("\n--- MÉTODO 3: Cálculo do Leff Efetivo (Proposta do Autor) ---")
    print("Objetivo: Encontrar o comprimento de apoio efetivo máximo, considerando todos os limites.")

    mn = Fb_pascals * modulo_de_seccao
    vn = (Fv_pascals * B * H) / 1.5

    a_flexao = qa_pascals * B
    b_flexao = (-2 * qa_pascals * B * C) - w_newtons
    c_flexao = (qa_pascals * B * C ** 2) + (2 * C * w_newtons) - (8 * mn)
    discriminante_flexao = b_flexao ** 2 - 4 * a_flexao * c_flexao
    leff_flexao = float('inf')
    if discriminante_flexao >= 0:
        leff_flexao = (-b_flexao + math.sqrt(discriminante_flexao)) / (2 * a_flexao)

    a_cisalhamento = qa_pascals * B
    b_cisalhamento = (-2 * vn) - (qa_pascals * B * C) - (2 * qa_pascals * B * H) - w_newtons
    c_cisalhamento = (w_newtons * C) + (2 * w_newtons * H)
    discriminante_cisalhamento = b_cisalhamento ** 2 - 4 * a_cisalhamento * c_cisalhamento
    leff_cisalhamento = float('inf')
    if discriminante_cisalhamento >= 0:
        leff_cisalhamento = (-b_cisalhamento + math.sqrt(discriminante_cisalhamento)) / (2 * a_cisalhamento)

    termo_interno = (0.06 * E_pascals * momento_de_inercia) / (0.9 * qa_pascals * B)
    lc_deflexao = termo_interno ** (1 / 3.0)
    leff_deflexao = (2 * lc_deflexao) + C

    leff_final = min(leff_flexao, leff_cisalhamento, leff_deflexao, L)

    print(f"Leff baseado na Flexão: {leff_flexao:.4f} m")
    print(f"Leff baseado no Cisalhamento: {leff_cisalhamento:.4f} m")
    print(f"Leff baseado na Deflexão: {leff_deflexao:.4f} m")
    print(f"Comprimento real da base (L): {L:.4f} m")
    print("-" * 40)
    print(f"O Comprimento de Apoio Efetivo (Leff) final é: {leff_final:.4f} m")


# --- FUNÇÃO PRINCIPAL ---
def main():
    print("--- ANÁLISE COMPLETA DE BASES DE GRUA (3 MÉTODOS) ---")
    print("Por favor, insira os valores nas unidades indicadas.")
    print("-" * 70)

    # Coleta de dados com as novas variáveis
    C = obter_entrada_numerica("C - Largura da Sapata [m]: ")
    F = obter_entrada_numerica("F - Carga Aplicada [t]: ")
    S_soil = obter_entrada_numerica("S - Tensão Admissível do Solo [kgf/cm²]: ")
    L = obter_entrada_numerica("L - Comprimento [m]: ")
    B = obter_entrada_numerica("B - Largura [m]: ")
    H = obter_entrada_numerica("H - Altura do mats [m]: ")
    rho = obter_entrada_numerica("ρ - Densidade [kg/m³]: ")
    Fb = obter_entrada_numerica("Fb - Tensão Flexão [MPa]: ")
    Fv = obter_entrada_numerica("Fv - Tensão Cisalhamento [MPa]: ")
    E_gpa = obter_entrada_numerica("E - Módulo de Elasticidade [GPa]: ")

    # --- Cálculos e Conversões ---
    volume = L * B * H
    massa_kg = volume * rho
    w_newtons = massa_kg * 9.81

    p_newtons = F * 9810
    qa_pascals = S_soil * 98100
    Fb_pascals = Fb * 1e6
    Fv_pascals = Fv * 1e6
    E_pascals = E_gpa * 1e9

    print("\n--- A calcular... ---")
    print(f"(Nota: Peso próprio da base calculado em {w_newtons / 9810:.2f} tf)")

    modulo_de_seccao = (B * H ** 2) / 6
    momento_de_inercia = (B * H ** 3) / 12

    # --- Execução das Análises ---
    calcular_metodo_capacidade_solo(p_newtons, w_newtons, qa_pascals, B, H, Fb_pascals, Fv_pascals, modulo_de_seccao)
    calcular_metodo_resistencia_base(p_newtons, w_newtons, qa_pascals, B, C, H, Fb_pascals, Fv_pascals, modulo_de_seccao)
    calcular_metodo_leff_efetivo(qa_pascals, w_newtons, L, B, H, C, Fb_pascals, Fv_pascals, E_pascals, modulo_de_seccao, momento_de_inercia)

    print("-" * 70)
    print("Análise concluída.")


if __name__ == "__main__":
    main()