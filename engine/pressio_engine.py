import math

# ==============================================================================
# PASSO 1: CAPTURA DE DADOS DE ENTRADA
# ==============================================================================
def capturar_dados_de_entrada(dados_da_revisao):
    """
    Captura os dados brutos do dicionário vindo da web, limpa os
    valores e os converte para o tipo float. Nenhuma conversão de
    unidade é feita aqui.
    """
    dados_capturados = {
        'C_ft': float(dados_da_revisao.get('c', '0').replace(',', '.')),
        'F_lb': float(dados_da_revisao.get('p_tf', '0').replace(',', '.')),
        'S_psf': float(dados_da_revisao.get('qa', '0').replace(',', '.')),
        'L_ft': float(dados_da_revisao.get('l_real', '0').replace(',', '.')),
        'W_ft': float(dados_da_revisao.get('b', '0').replace(',', '.')),
        'T_ft': float(dados_da_revisao.get('d', '0').replace(',', '.')),
        'rho_lb_ft3': float(dados_da_revisao.get('densidade', '0').replace(',', '.')),
        'Fb_psi': float(dados_da_revisao.get('fb', '0').replace(',', '.')),
        'Fv_psi': float(dados_da_revisao.get('fv', '0').replace(',', '.')),
        'E_ksi': float(dados_da_revisao.get('e_gpa', '0').replace(',', '.'))
    }
    return dados_capturados

# ==============================================================================
# PASSO 2: CONVERSÃO DE UNIDADES (IMPERIAL -> SI)
# ==============================================================================
def converter_imperial_para_si(dados_imperiais):
    """
    Converte dados imperiais para o Sistema Internacional (SI) para os cálculos.
    Recebe o dicionário da função capturar_dados_de_entrada.
    """
    # --- Fatores de Conversão (Imperial para SI) ---
    FT_PARA_M = 0.3048
    LBF_PARA_NEWTON = 4.44822
    PSF_PARA_PASCAL = 47.88026
    LB_FT3_PARA_KG_M3 = 16.0185
    PSI_PARA_PASCAL = 6894.76
    KSI_PARA_PASCAL = 6.89476e6

    # Converte as dimensões para metros (m)
    C_m = dados_imperiais['C_ft'] * FT_PARA_M
    L_m = dados_imperiais['L_ft'] * FT_PARA_M
    B_m = dados_imperiais['W_ft'] * FT_PARA_M
    H_m = dados_imperiais['T_ft'] * FT_PARA_M
    
    # Calcula propriedades geométricas e de massa em SI
    volume_m3 = L_m * B_m * H_m
    densidade_kg_m3 = dados_imperiais['rho_lb_ft3'] * LB_FT3_PARA_KG_M3
    massa_kg = volume_m3 * densidade_kg_m3
    
    # Monta o dicionário de saída com todas as variáveis em SI
    dados_si = {
        'C': C_m,
        'L': L_m,
        'B': B_m,
        'H': H_m,
        'p_newtons': dados_imperiais['F_lb'] * LBF_PARA_NEWTON,
        'qa_pascals': dados_imperiais['S_psf'] * PSF_PARA_PASCAL,
        'Fb_pascals': dados_imperiais['Fb_psi'] * PSI_PARA_PASCAL,
        'Fv_pascals': dados_imperiais['Fv_psi'] * PSI_PARA_PASCAL,
        'E_pascals': dados_imperiais['E_ksi'] * KSI_PARA_PASCAL,
        'w_newtons': massa_kg * 9.80665,  # Usando g padrão
        'modulo_de_seccao': (B_m * H_m ** 2) / 6,
        'momento_de_inercia': (B_m * H_m ** 3) / 12,
    }
    return dados_si

# ==============================================================================
# PASSO 3: FUNÇÕES DE CÁLCULO (Motor principal, operando em SI)
# ==============================================================================
def calcular_metodo_leff_efetivo(dados_si):
    """Calcula o comprimento efetivo por três critérios e retorna os resultados em metros."""
    qa_pascals = dados_si['qa_pascals']
    w_newtons = dados_si['w_newtons']
    L, B, H, C = dados_si['L'], dados_si['B'], dados_si['H'], dados_si['C']
    Fb_pascals = dados_si['Fb_pascals']
    Fv_pascals = dados_si['Fv_pascals']
    E_pascals = dados_si['E_pascals']
    modulo_de_seccao = dados_si['modulo_de_seccao']
    momento_de_inercia = dados_si['momento_de_inercia']

    # Resistência do Mat à Flexão (Mn) e Cisalhamento (Vn)
    mn = Fb_pascals * modulo_de_seccao
    vn = (Fv_pascals * B * H) / 1.5
    
    # Critério de Flexão (Eq. 19 do paper)
    a_flexao = qa_pascals * B
    b_flexao = (-2 * qa_pascals * B * C) - w_newtons
    c_flexao = (qa_pascals * B * C**2) + (2 * C * w_newtons) - (8 * mn)
    discriminante_flexao = b_flexao**2 - 4 * a_flexao * c_flexao
    leff_flexao = float('inf')
    if discriminante_flexao >= 0 and a_flexao != 0:
        leff_flexao = (-b_flexao + math.sqrt(discriminante_flexao)) / (2 * a_flexao)
        
    # Critério de Cisalhamento (Eq. 22 do paper)
    a_cisalhamento = qa_pascals * B
    b_cisalhamento = (-2 * vn) - (qa_pascals * B * C) - (2 * qa_pascals * B * H) - w_newtons
    c_cisalhamento = (w_newtons * C) + (2 * w_newtons * H)
    discriminante_cisalhamento = b_cisalhamento**2 - 4 * a_cisalhamento * c_cisalhamento
    leff_cisalhamento = float('inf')
    if discriminante_cisalhamento >= 0 and a_cisalhamento != 0:
        leff_cisalhamento = (-b_cisalhamento + math.sqrt(discriminante_cisalhamento)) / (2 * a_cisalhamento)
        
    # Critério de Deflexão (Eq. 28 do paper)
    termo_interno_deflexao = (0.06 * E_pascals * momento_de_inercia) / (0.9 * qa_pascals * B) if (0.9 * qa_pascals * B) > 0 else 0
    lc_deflexao = termo_interno_deflexao**(1/3.0)
    leff_deflexao = (2 * lc_deflexao) + C
    
    return {
        "leff_flexao_m": leff_flexao,
        "leff_cisalhamento_m": leff_cisalhamento,
        "leff_deflexao_m": leff_deflexao,
    }

def calcular_metricas_resumo(perc_comprimento_ativo, qt_operacao_pa, qa_pascals):
    """Calcula percentuais de utilização para o resumo."""
    perc_capacidade_solo = (qt_operacao_pa / qa_pascals) * 100 if qa_pascals > 0 else 0
    return {
        'perc_comprimento_ativo': f"{perc_comprimento_ativo:.1f}",
        'perc_capacidade_solo': f"{perc_capacidade_solo:.1f}"
    }

def calcular_comparativos_pressao(p_newtons, w_newtons, L, B, C, H):
    """Calcula pressões comparativas e retorna em Pascals (Pa)."""
    area_total = L * B
    pressao_total_pa = (p_newtons + w_newtons) / area_total if area_total > 0 else 0
    
    largura_dispersa = C + 2 * H
    area_dispersa = largura_dispersa * largura_dispersa
    pressao_dispersa_pa = (p_newtons + w_newtons) / area_dispersa if area_dispersa > 0 else 0
    
    return {
        'pressao_total_pa': pressao_total_pa,
        'pressao_dispersa_pa': pressao_dispersa_pa
    }

# ==============================================================================
# PASSO 4: CONVERSÃO DE UNIDADES (SI -> IMPERIAL)
# ==============================================================================
def converter_si_para_imperial(resultados_si):
    """
    Converte os resultados finais do cálculo (em SI) para unidades
    imperiais, já formatando como texto para exibição na interface.
    
    Args:
        resultados_si (dict): Dicionário com os valores de resultado em SI.

    Returns:
        dict: Dicionário com os resultados formatados como strings em unidades imperiais.
    """
    # --- Fatores de Conversão (SI para Imperial) ---
    M_PARA_FT = 3.28084
    PASCAL_PARA_PSF = 0.0208854
    MM_PARA_IN = 0.0393701
    
    # Cria um novo dicionário para os resultados formatados
    resultados_formatados = {
        "analises_leff": [],
        "resumo_comparativo": {}
    }
    
    # Itera sobre as análises de Leff para converter e formatar
    for analise in resultados_si['analises_leff']:
        leff_ft = analise['leff_m'] * M_PARA_FT
        pressao_psf = analise['pressao_pa'] * PASCAL_PARA_PSF
        deformacao_in = analise['deformacao_mm'] * MM_PARA_IN
        
        # Adiciona ao novo dicionário com as strings formatadas
        resultados_formatados['analises_leff'].append({
            'titulo': analise['titulo'],
            'leff': f"{leff_ft:.2f} ft",
            'pressao_gerada': f"{pressao_psf:.0f} psf",
            'deformacao': f"{deformacao_in:.2f} in",
            'is_governing': analise['is_governing'],
        })

    # Converte os resultados do resumo comparativo
    resumo_si = resultados_si['resumo_comparativo']
    
    # Copia os valores que não precisam de conversão (percentuais, status, etc.)
    # e converte os que precisam
    resultados_formatados['resumo_comparativo'] = {
        **resumo_si,
        'pressao_total_psf': f"{(resumo_si.pop('pressao_total_pa') * PASCAL_PARA_PSF):.0f}",
        'pressao_dispersa_psf': f"{(resumo_si.pop('pressao_dispersa_pa') * PASCAL_PARA_PSF):.0f}",
    }

    return resultados_formatados

# ==============================================================================
# PASSO 5: FUNÇÃO PRINCIPAL ORQUESTRADORA
# ==============================================================================
def realizar_analise_completa(dados_entrada_imp):
    """
    Orquestra a análise completa: captura, converte, calcula e formata os resultados.
    
    Args:
        dados_entrada_imp (dict): Dicionário com os dados brutos do formulário.

    Returns:
        dict: Dicionário com o resultado final da análise ou uma mensagem de erro.
    """
    try:
        # 1. Captura e limpa os dados da web
        dados_capturados = capturar_dados_de_entrada(dados_entrada_imp)
        
        # 2. Converte as entradas de Imperial para SI
        dados_si = converter_imperial_para_si(dados_capturados)

        # 3. Executa os cálculos principais em SI
        resultados_leff_si = calcular_metodo_leff_efetivo(dados_si)
        
        # Encontra o comprimento efetivo governante (o menor valor válido)
        leff_minimo_m = min(r for r in resultados_leff_si.values() if r is not None and r != float('inf'))

        qt_operacao_pa = (dados_si['p_newtons'] + dados_si['w_newtons']) / (leff_minimo_m * dados_si['B']) if (leff_minimo_m * dados_si['B']) > 0 else 0
        perc_comprimento_ativo = (leff_minimo_m / dados_si['L']) * 100 if dados_si['L'] > 0 else 0
        
        # 4. Monta um dicionário com todos os resultados brutos em SI
        resultados_em_si = {"analises_leff": [], "resumo_comparativo": {}}
        
        leff_types = [
            ("Bending", resultados_leff_si['leff_flexao_m']),
            ("Shear", resultados_leff_si['leff_cisalhamento_m']),
            ("Deflection", resultados_leff_si['leff_deflexao_m'])
        ]
        
        for nome, leff_m in leff_types:
            pressao_pa, deformacao_mm = 0, 0
            if leff_m is not None and leff_m != float('inf') and dados_si['B'] > 0:
                pressao_pa = (dados_si['p_newtons'] + dados_si['w_newtons']) / (leff_m * dados_si['B'])
                lc_m = (leff_m - dados_si['C']) / 2.0
                q_pa_carga = dados_si['p_newtons'] / (leff_m * dados_si['B'])
                numerador = q_pa_carga * dados_si['B'] * (lc_m ** 4)
                denominador = 8 * dados_si['E_pascals'] * dados_si['momento_de_inercia']
                if denominador > 0:
                    deformacao_mm = ((numerador / denominador) * 1000)

            resultados_em_si['analises_leff'].append({
                'titulo': f"{nome} Limit",
                'leff_m': leff_m,
                'pressao_pa': pressao_pa,
                'deformacao_mm': deformacao_mm,
                'is_governing': (leff_m == leff_minimo_m),
            })
        
        resumo_metricas = calcular_metricas_resumo(perc_comprimento_ativo, qt_operacao_pa, dados_si['qa_pascals'])
        resumo_comparativos_pa = calcular_comparativos_pressao(dados_si['p_newtons'], dados_si['w_newtons'], dados_si['L'], dados_si['B'], dados_si['C'], dados_si['H'])
        resultados_em_si['resumo_comparativo'] = {**resumo_metricas, **resumo_comparativos_pa}
        
        # 5. Converte todos os resultados de SI para Imperial para exibição
        resultados_finais_formatados = converter_si_para_imperial(resultados_em_si)
        
        # Adiciona a lógica de status final ao dicionário já formatado
        cond_falha_comprimento = leff_minimo_m > dados_si['L']
        perc_solo_float = float(resultados_finais_formatados['resumo_comparativo']['perc_capacidade_solo'])
        cond_falha_solo = perc_solo_float > 100.0

        
        # ==========================================================
        # --- BLOCO DE DEBUG: Adicione ou substitua por este trecho ---
        print("="*30)
        print("INICIANDO DEBUG DO STATUS FINAL")
        print(f"Leff Mínimo Necessário (m): {leff_minimo_m}")
        print(f"Comprimento do Mat (m): {dados_si['L']}")
        print(f"Condição de Falha por Comprimento (Leff > L)? -> {cond_falha_comprimento}")
        print("-" * 20)
        print(f"Percentual do Solo Utilizado (%): {perc_solo_float}")
        print(f"Condição de Falha por Solo (% > 100)? -> {cond_falha_solo}")
        print("-" * 20)
        
        status_final = "FAIL" if cond_falha_comprimento or cond_falha_solo else "APPROVED"
        print(f"Resultado do 'or': {cond_falha_comprimento or cond_falha_solo}")
        print(f"Status Final Calculado: {status_final}")
        print("FIM DO DEBUG DO STATUS FINAL")
        print("="*30)
        # --- FIM DO BLOCO DE DEBUG ---
        # ==========================================================

        resultados_finais_formatados['resumo_comparativo'].update({
            'status_geral': "FAIL" if cond_falha_comprimento or cond_falha_solo else "APPROVED",
            'falha_por': 'length' if cond_falha_comprimento else ('soil' if cond_falha_solo else 'none'),
            'perc_comprimento_ativo_raw': perc_comprimento_ativo,
            'perc_capacidade_solo_raw': perc_solo_float
        })

        return {"sucesso": True, "resultados": resultados_finais_formatados}

    except (ValueError, KeyError, TypeError, ZeroDivisionError) as e:
        return {"erro": f"Error during analysis: {e}", "sucesso": False}