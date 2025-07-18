# -*- coding: utf-8 -*-
import math

"""
Script para análise de bases de grua (Crane Mats) usando 3 MÉTODOS
baseado no paper "Effective Bearing Length of Crane Mats" de David Duerr.

Versão final com estrutura de entrada de dados profissional e unidades de medida
personalizadas para o padrão de mercado e da NBR 7190.
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
def calcular_metodo_capacidade_solo(p_newtons, w_newtons, qa_pascals, b, d, fb_pascals, fv_pascals, modulo_de_seccao):
    print("\n--- MÉTODO 1: Análise baseada na Capacidade do Solo ---")
    print("Objetivo: Dimensionar a base para que o solo não falhe, e verificar as tensões na base.")

    a_reqd = (p_newtons + w_newtons) / qa_pascals
    l_reqd = a_reqd / b
    lc = l_reqd / 2.0
    q_p = p_newtons / (l_reqd * b)
    m = (q_p * b) * (lc ** 2) / 2
    f_b_calc = m / modulo_de_seccao if modulo_de_seccao > 0 else 0
    v = (q_p * b) * (lc - d)
    f_v_calc = (1.5 * v) / (b * d) if (b * d) > 0 else 0

    print(f"Comprimento de apoio necessário (L_reqd): {l_reqd:.2f} m")
    print(f"Tensão de flexão resultante (fb): {f_b_calc / 1e6:.2f} MPa (Admissível: {fb_pascals / 1e6:.2f} MPa)")
    print(f"Tensão de cisalhamento resultante (fv): {f_v_calc / 1e6:.2f} MPa (Admissível: {fv_pascals / 1e6:.2f} MPa)")
    if f_b_calc <= fb_pascals and f_v_calc <= fv_pascals:
        print("Resultado: A base RESISTE às tensões para este comprimento.")
    else:
        print("Resultado: A base NÃO RESISTE às tensões para este comprimento.")


# --- MÉTODO 2: BASEADO NA RESISTÊNCIA DA BASE (VERSÃO COMPLETA) ---
def calcular_metodo_resistencia_base(p_newtons, w_newtons, qa_pascals, b, c, d, fb_pascals, fv_pascals,
                                     modulo_de_seccao):
    print("\n--- MÉTODO 2: Análise baseada na Resistência da Base (Flexão e Cisalhamento) ---")
    print("Objetivo: Encontrar o Leff limitante da base e verificar se o solo suporta.")

    m_max = fb_pascals * modulo_de_seccao
    a_flex = p_newtons
    b_flex = -2 * p_newtons * c - 8 * m_max
    c_flex = p_newtons * c ** 2
    discriminante_flex = b_flex ** 2 - 4 * a_flex * c_flex
    leff_flexao = float('inf')
    if discriminante_flex >= 0:
        leff_flexao = (-b_flex + math.sqrt(discriminante_flex)) / (2 * a_flex)

    vn_max = (fv_pascals * b * d) / 1.5
    leff_cisalhamento = float('inf')
    if p_newtons > 2 * vn_max:
        leff_cisalhamento = (p_newtons * (c + 2 * d)) / (p_newtons - 2 * vn_max)

    leff = min(leff_flexao, leff_cisalhamento)
    modo_de_falha = "Flexão" if leff == leff_flexao else "Cisalhamento"

    print(f"Leff limitado pela Flexão: {leff_flexao:.2f} m")
    print(f"Leff limitado pelo Cisalhamento: {leff_cisalhamento:.2f} m")
    print(f"Modo de falha governante da base: {modo_de_falha} em Leff = {leff:.2f} m")

    q_t = (p_newtons + w_newtons) / (leff * b) if leff > 0 else 0
    print(f"Pressão resultante no solo (qt): {q_t / 1e6:.4f} MPa (Admissível: {qa_pascals / 1e6:.4f} MPa)")

    if q_t <= qa_pascals:
        print("Resultado: O solo RESISTE à pressão para esta configuração.")
    else:
        print("Resultado: O solo NÃO RESISTE à pressão para esta configuração.")


# --- MÉTODO 3: CÁLCULO DO LEFF EFETIVO (PROPOSTA DO AUTOR) ---
def calcular_metodo_leff_efetivo(qa_pascals, w_newtons, l_real, b, d, c, fb_pascals, fv_pascals, e_pascals,
                                 modulo_de_seccao, momento_de_inercia):
    print("\n--- MÉTODO 3: Cálculo do Leff Efetivo (Proposta do Autor) ---")
    print("Objetivo: Encontrar o comprimento de apoio efetivo máximo, considerando todos os limites.")

    mn = fb_pascals * modulo_de_seccao
    vn = (fv_pascals * b * d) / 1.5

    a_flexao = qa_pascals * b
    b_flexao = (-2 * qa_pascals * b * c) - w_newtons
    c_flexao = (qa_pascals * b * c ** 2) + (2 * c * w_newtons) - (8 * mn)
    discriminante_flexao = b_flexao ** 2 - 4 * a_flexao * c_flexao
    leff_flexao = float('inf')
    if discriminante_flexao >= 0:
        leff_flexao = (-b_flexao + math.sqrt(discriminante_flexao)) / (2 * a_flexao)

    a_cisalhamento = qa_pascals * b
    b_cisalhamento = (-2 * vn) - (qa_pascals * b * c) - (2 * qa_pascals * b * d) - w_newtons
    c_cisalhamento = (w_newtons * c) + (2 * w_newtons * d)
    discriminante_cisalhamento = b_cisalhamento ** 2 - 4 * a_cisalhamento * c_cisalhamento
    leff_cisalhamento = float('inf')
    if discriminante_cisalhamento >= 0:
        leff_cisalhamento = (-b_cisalhamento + math.sqrt(discriminante_cisalhamento)) / (2 * a_cisalhamento)

    termo_interno = (0.06 * e_pascals * momento_de_inercia) / (0.9 * qa_pascals * b)
    lc_deflexao = termo_interno ** (1 / 3.0)
    leff_deflexao = (2 * lc_deflexao) + c

    leff_final = min(leff_flexao, leff_cisalhamento, leff_deflexao, l_real)

    print(f"Leff baseado na Flexão: {leff_flexao:.4f} m")
    print(f"Leff baseado no Cisalhamento: {leff_cisalhamento:.4f} m")
    print(f"Leff baseado na Deflexão: {leff_deflexao:.4f} m")
    print(f"Comprimento real da base (l_real): {l_real:.4f} m")
    print("-" * 40)
    print(f"O Comprimento de Apoio Efetivo (Leff) final é: {leff_final:.4f} m")


# --- FUNÇÃO PRINCIPAL ---
def main():
    print("--- ANÁLISE COMPLETA DE BASES DE GRUA (3 MÉTODOS) ---")
    print("Por favor, insira os valores nas unidades indicadas.")
    print("-" * 70)

    # Coleta de dados conforme nova estrutura
    print("--- Dados do Guindaste ---")
    c = obter_entrada_numerica("Largura da Sapata da Grua (C) [metros - m]: ")
    p_tf = obter_entrada_numerica("Carga da Sapata sobre a base (P) [toneladas-força - tf]: ")

    print("\n--- Dados Geométricos da Base ---")
    l_real = obter_entrada_numerica("Comprimento da Base (L) [metros - m]: ")
    b = obter_entrada_numerica("Largura da Base (B) [metros - m]: ")
    d = obter_entrada_numerica("Altura da Base (d) [metros - m]: ")
    densidade = obter_entrada_numerica("Densidade do material (ρ) [kg/m³]: ")

    print("\n--- Propriedades Mecânicas da Base ---")
    fb = obter_entrada_numerica("Tensão Admissível à Flexão (Fb) [MPa]: ")
    fv = obter_entrada_numerica("Tensão Admissível ao Cisalhamento (Fv) [MPa]: ")
    e = obter_entrada_numerica("Módulo de Elasticidade (E) [GPa]: ")

    print("\n--- Propriedades Mecânicas do Solo ---")
    qa = obter_entrada_numerica("Pressão Admissível do Solo (qa) [kgf/cm²]: ")

    # --- Cálculos e Conversões ---
    volume = l_real * b * d
    massa_kg = volume * densidade
    w_newtons = massa_kg * 9.81

    p_newtons = p_tf * 9810
    qa_pascals = qa * 98100
    fb_pascals = fb * 1e6
    fv_pascals = fv * 1e6
    e_pascals = e * 1e9

    print("\n--- A calcular... ---")
    print(f"(Nota: Peso próprio da base calculado em {w_newtons / 9810:.2f} tf)")

    modulo_de_seccao = (b * d ** 2) / 6
    momento_de_inercia = (b * d ** 3) / 12

    # --- Execução das Análises ---
    calcular_metodo_capacidade_solo(p_newtons, w_newtons, qa_pascals, b, d, fb_pascals, fv_pascals, modulo_de_seccao)
    calcular_metodo_resistencia_base(p_newtons, w_newtons, qa_pascals, b, c, d, fb_pascals, fv_pascals,
                                     modulo_de_seccao)
    calcular_metodo_leff_efetivo(qa_pascals, w_newtons, l_real, b, d, c, fb_pascals, fv_pascals, e_pascals,
                                 modulo_de_seccao, momento_de_inercia)

    print("-" * 70)
    print("Análise concluída.")


if __name__ == "__main__":
    main()