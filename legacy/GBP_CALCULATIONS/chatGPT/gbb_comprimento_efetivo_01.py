#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Validação do Método do Comprimento Efetivo (v1.6)
Agora com seleção de tipo de solo para k_s ou entrada manual.
"""


def parse_float(prompt):
    """Lê um float do usuário, aceitando vírgula ou ponto como decimal."""
    while True:
        s = input(prompt).strip().replace(',', '.')
        try:
            return float(s)
        except ValueError:
            print(
                'Entrada inválida. Digite um número '
                '(use vírgula ou ponto para decimais).'
            )


def select_soil_ks():
    """
    Apresenta menu de solos com seus intervalos típicos de k_s (kN/m³).
    Retorna o valor médio do intervalo ou, se escolher '0', pede entrada manual.
    """
    soils = {
        '1': ('Argila mole',       5_000,   15_000),
        '2': ('Argila compacta',   15_000,  30_000),
        '3': ('Areia fofa',        10_000,  25_000),
        '4': ('Areia média compacta', 25_000, 50_000),
        '5': ('Areia compacta',    50_000, 150_000),
        '6': ('Pedregulho',        100_000, 300_000),
    }

    print('\nSelecione o tipo de solo para obter k_s médio:')
    for key, (name, lo, hi) in soils.items():
        print(f'  {key}. {name} ({lo:,}–{hi:,} kN/m³)')
    print('  0. Digitar k_s manualmente')

    choice = input('Opção [0-6]: ').strip()
    if choice in soils:
        lo, hi = soils[choice][1], soils[choice][2]
        ks = (lo + hi) / 2
        print(f'→ k_s médio para {soils[choice][0]} = {ks:,.0f} kN/m³\n')
        return ks
    else:
        return parse_float('k_s (kN/m³): ')


def main():
    print('=== Método do Comprimento Efetivo - v1.6 ===\n')

    # 1) Entrada P_adm e cálculo de p_lim
    padm = parse_float('Pressão admissível P_adm (kgf/cm²): ')
    padm_pa = padm * 98066.5
    limit_fraction = parse_float('Fração limite p_lim (ex: 0.10 para 10%): ')
    p_lim = padm_pa * limit_fraction

    # 2) Seleção ou entrada de k_s
    ks_kn = select_soil_ks()           # em kN/m³
    ks = ks_kn * 1e3                   # → N/m³

    # 3) Demais entradas geométricas e materiais
    carga_t = parse_float('Carga aplicada F (toneladas métricas): ')
    length = parse_float('Comprimento do mats L (m): ')
    width = parse_float('Largura do mats B (m): ')
    thickness = parse_float('Espessura do mats t (m): ')
    modulus = parse_float('Módulo de elasticidade E (GPa): ')
    inertia = parse_float('Momento de inércia I (m⁴): ')

    # 4) Conversões
    F = carga_t * 1000                 # kN
    E = modulus * 1e9                  # Pa
    area = length * width              # m²

    # 5) Exibir dados
    print('\n=== Dados Convertidos ===')
    print(f'P_adm     = {padm:.3f} kgf/cm² → {padm_pa:.3f} Pa')
    print(f'p_lim     = {p_lim:.3f} Pa')
    print(f'k_s       = {ks_kn:,.0f} kN/m³ → {ks:,.3e} N/m³')
    print(f'F         = {F:.3f} kN')
    print(f'L × B     = {length:.3f} m × {width:.3f} m = {area:.3f} m²')
    print(f't         = {thickness:.3f} m')
    print(f'E         = {E:.3e} Pa')
    print(f'I         = {inertia:.6e} m⁴')

    # 6) Cálculo de RR e L_eff
    rr = (E * inertia) / (ks * area)
    l_eff = length * (rr ** 0.25)

    print('\n=== Resultados ===')
    print(f'Rigidez Relativa (RR)     = {rr:.6e}')
    print(f'Comprimento Efetivo (L_eff)= {l_eff:.6f} m\n')

    print(
        '> Observação: L_eff é estimativa inicial. '
        'Na próxima versão, implementaremos Eq. 5 completa.'
    )


if __name__ == '__main__':
    main()
