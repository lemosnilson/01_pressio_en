import math
import locale


def tratar_entrada_numero(mensagem):
    """Solicita entrada do usuário e converte para float, tratando vírgulas e pontos decimais"""
    while True:
        try:
            entrada = input(mensagem).strip()
            # Substitui vírgulas por pontos e remove espaços
            entrada = entrada.replace(',', '.').replace(' ', '')
            # Verifica se há múltiplos pontos decimais
            if entrada.count('.') > 1:
                raise ValueError("Formato inválido: múltiplos pontos decimais")
            return float(entrada)
        except ValueError as e:
            print(f"Entrada inválida! Use números (ex: 10,5 ou 10.5). Erro: {e}")


def gpa_para_kgfcm2(gpa):
    """Converte GPa para kgf/cm²"""
    # 1 GPa = 1,000,000,000 N/m²
    # 1 kgf/cm² = 98,066.5 N/m²
    return gpa * 1e9 / 98066.5


def main():
    print("=" * 50)
    print("ANÁLISE DE TENSÃO EM SOLO PARA GUINDASTES")
    print("=" * 50)

    # Configurar localidade para português
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

    try:
        # Informações do guindaste
        print("\n[INFORMAÇÕES DO GUINDASTE]")
        long = tratar_entrada_numero("Distância longitudinal entre patolas (cm): ")
        trans = tratar_entrada_numero("Distância transversal entre patolas (cm): ")
        P = tratar_entrada_numero("Carga na patola mais solicitada (kgf): ")

        # Validar valores positivos
        if any(val <= 0 for val in [long, trans, P]):
            raise ValueError("Valores devem ser positivos!")

        # Dados dos mats
        print("\n[DADOS DOS MATS]")
        L = tratar_entrada_numero("Comprimento total dos mats (cm): ")
        b = tratar_entrada_numero("Largura dos mats (cm): ")
        h = tratar_entrada_numero("Altura/espessura dos mats (cm): ")
        E_gpa = tratar_entrada_numero("Módulo de elasticidade da madeira (GPa): ")

        # Validar dimensões
        if any(val <= 0 for val in [L, b, h, E_gpa]):
            raise ValueError("Dimensões devem ser positivas!")

        # Converter módulo de elasticidade para kgf/cm²
        E_m = gpa_para_kgfcm2(E_gpa)
        print(f"  > Módulo convertido: {E_m:,.2f} kgf/cm²")

        # Dados do solo
        print("\n[DADOS DO SOLO]")
        sigma_adm = tratar_entrada_numero("Resistência do solo (kgf/cm²): ")
        if sigma_adm <= 0:
            raise ValueError("Resistência do solo deve ser positiva!")

        # Cálculo da distância diagonal entre patolas
        diagonal = math.sqrt(long ** 2 + trans ** 2)
        print(f"\nDistância diagonal entre patolas: {diagonal:.2f} cm")

        # Cálculo do recalque máximo admissível (Δ)
        delta_max = diagonal * math.tan(math.radians(1))  # em cm
        print(f"Recalque máximo admissível (1° inclinação): {delta_max:.4f} cm")

        # Cálculo do coeficiente de reação do solo (ks)
        ks = sigma_adm / delta_max
        print(f"Coeficiente de reação do solo (ks): {ks:.6f} kgf/cm³")

        # Cálculo do momento de inércia (Im)
        Im = (b * h ** 3) / 12
        print(f"\nMomento de inércia dos mats (Im): {Im:,.2f} cm⁴")

        # Cálculo do comprimento efetivo
        L_efetivo = (4 * E_m * Im / ks) ** 0.25
        print(f"Comprimento efetivo (L_efetivo): {L_efetivo:,.2f} cm")

        # Verificação da rigidez
        if L <= 2 * L_efetivo:
            print("\nClassificação: MATS RÍGIDO (tensão uniforme)")
            sigma_max = P / (b * L)
        else:
            print("\nClassificação: MATS FLEXÍVEL (tensão máxima no centro)")
            beta = 1 / L_efetivo
            sigma_max = (P * beta) / (2 * b)

        # Resultado final
        print(f"\nTensão máxima calculada: {sigma_max:.4f} kgf/cm²")
        print(f"Resistência do solo: {sigma_adm:.4f} kgf/cm²")

        if sigma_max <= sigma_adm:
            print("\n✅ SOLO SEGURO! Tensão máxima ≤ Resistência do solo")
            print(f"Margem de segurança: {((sigma_adm - sigma_max) / sigma_adm) * 100:.2f}%")
        else:
            print("\n⛔ SOLO EM RISCO! Tensão máxima > Resistência do solo")
            deficit = (sigma_max / sigma_adm - 1) * 100
            print(f"Excesso de tensão: {deficit:.2f}%")
            print(f"Necessário aumentar área ou rigidez dos mats!")

    except Exception as e:
        print(f"\n❌ ERRO: {str(e)}")
        print("Verifique os dados de entrada e tente novamente.")


if __name__ == "__main__":
    main()