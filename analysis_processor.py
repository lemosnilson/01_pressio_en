# analysis_processor.py

from engine.pressio_engine import realizar_analise_completa

def processar_analise_para_relatorio(dados_entrada):
    """
    Esta função serve como uma camada sobre o engine original.
    1. Chama o engine homologado.
    2. Realiza cálculos adicionais para o relatório de sensibilidade.
    """

    # --- 1. CHAMA O ENGINE ORIGINAL E VERIFICA O SUCESSO ---
    resultado_bruto = realizar_analise_completa(dados_entrada)

    if not resultado_bruto.get('sucesso'):
        return resultado_bruto

    # --- 2. EXTRAI OS DADOS NECESSÁRIOS DO RESULTADO BRUTO E DOS DADOS DE ENTRADA ---
    try:
        # Recalcula as variáveis base para os cálculos do relatório
        C = float(dados_entrada.get('c', 0).replace(',', '.'))
        L_real = float(dados_entrada.get('l_real', 0).replace(',', '.'))
        B = float(dados_entrada.get('b', 0).replace(',', '.'))
        H = float(dados_entrada.get('d', 0).replace(',', '.'))
        F = float(dados_entrada.get('p_tf', 0).replace(',', '.'))
        qa_pascals = float(dados_entrada.get('qa', 0).replace(',', '.')) * 98100
        
        p_newtons = F * 9810
        volume = L_real * B * H
        rho = float(dados_entrada.get('densidade', 0).replace(',', '.'))
        w_newtons = (volume * rho) * 9.81

        # Extrai os dados da lista 'analises_leff' que o engine retorna
        analises = resultado_bruto.get('analises_leff', [])
        
        leff_final = 0.0
        leff_flexao = 0.0
        leff_cisalhamento = 0.0
        leff_deformacao = 0.0

        for analise in analises:
            leff_valor_str = analise.get('leff', '0 m').replace(' m', '').replace(',', '.')
            leff_valor_float = float(leff_valor_str)

            if 'Flexão' in analise.get('titulo', ''):
                leff_flexao = leff_valor_float
            elif 'Cisalhamento' in analise.get('titulo', ''):
                leff_cisalhamento = leff_valor_float
            elif 'Deformação' in analise.get('titulo', ''):
                leff_deformacao = leff_valor_float
            
            if analise.get('is_governing'):
                leff_final = leff_valor_float
        
        if leff_final == 0.0 and all(v != 0.0 for v in [leff_flexao, leff_cisalhamento, leff_deformacao]):
            leff_final = min(leff_flexao, leff_cisalhamento, leff_deformacao)
        
    except (ValueError, KeyError) as e:
        return {"sucesso": False, "erro": f"Erro ao processar dados: {e}"}

    # --- 3. EXECUTA OS NOVOS CÁLCULOS PARA O RELATÓRIO ---
    perc_comprimento_ativo = (leff_final / L_real) * 100 if L_real > 0 else 0
    qt_operacao = (p_newtons + w_newtons) / (leff_final * B) if (leff_final * B) > 0 else 0
    perc_capacidade_solo = (qt_operacao / qa_pascals) * 100 if qa_pascals > 0 else 0
    pressao_final_kgf = qt_operacao / 98066.5
    
    area_total = L_real * B
    pressao_total_pa = (p_newtons + w_newtons) / area_total if area_total > 0 else 0
    pressao_total_kgf = pressao_total_pa / 98066.5
    
    area_dispersa = (C + 2 * H)**2
    pressao_dispersa_pa = (p_newtons + w_newtons) / area_dispersa if area_dispersa > 0 else 0
    pressao_dispersa_kgf = pressao_dispersa_pa / 98066.5

    # --- 4. MONTA O DICIONÁRIO FINAL PARA O RELATÓRIO ---
    relatorio_final = {
        'leff_final': f"{leff_final:.2f}",
        'leff_flexao': f"{leff_flexao:.2f}",
        'leff_cisalhamento': f"{leff_cisalhamento:.2f}",
        'leff_deformacao': f"{leff_deformacao:.2f}",
        'perc_comprimento_ativo': f"{perc_comprimento_ativo:.1f}",
        'perc_capacidade_solo': f"{perc_capacidade_solo:.1f}",
        'pressao_total_kgf': f"{pressao_total_kgf:.2f}",
        'pressao_dispersa_kgf': f"{pressao_dispersa_kgf:.2f}",
        'pressao_final_kgf': f"{pressao_final_kgf:.2f}",
        'sucesso': True
    }
    return relatorio_final