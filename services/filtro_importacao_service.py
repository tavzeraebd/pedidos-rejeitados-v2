import os
import json
import glob
from datetime import datetime

def verificar_pedidos_nao_importados():
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    try:
        # 1. Localiza os arquivos mais recentes de hoje
        arq_relatorio = sorted(glob.glob(f"relatorios/relatorio_{hoje}.json"))[-1]
        arq_winthor = "winthor/pedidos_winthor_data.json" # Nome fixo conforme definido anteriormente

        if not os.path.exists(arq_winthor):
            print(f"Erro: Arquivo do WinThor não encontrado.")
            return None

    except IndexError:
        print(f"Erro: Relatório de hoje ({hoje}) não encontrado.")
        return None

    # 2. Carrega os dados
    with open(arq_relatorio, "r", encoding="utf-8") as f:
        dados_relatorio = json.load(f)
    
    with open(arq_winthor, "r", encoding="utf-8") as f:
        dados_winthor = json.load(f)

    # 3. Cria um Set com os números de pedidos do WinThor para busca ultra rápida
    # Convertemos para string para garantir a comparação correta
    pedidos_no_winthor = {str(item.get("NUMPEDRCA")) for item in dados_winthor}

    transacoes_fora_do_horario = []

    # 4. Compara codigoPedidoMaxima com NUMPEDRCA
    for trans in dados_relatorio.get("transacoes", []):
        codigo_maxima = str(trans.get("codigoPedidoMaxima", ""))
        
        # Se o código NÃO estiver no set do WinThor, adicionamos à lista
        if codigo_maxima not in pedidos_no_winthor:
            transacoes_fora_do_horario.append(trans)

    # 5. Salva o resultado para o serviço de e-mail
    diretorio_saida = "envia-email"
    if not os.path.exists(diretorio_saida):
        os.makedirs(diretorio_saida)

    caminho_saida = os.path.join(diretorio_saida, "fora_do_horario_data.json")
    
    resultado_final = {
        "data_verificacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_nao_importados": len(transacoes_fora_do_horario),
        "transacoes": transacoes_fora_do_horario
    }

    with open(caminho_saida, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=4, ensure_ascii=False)

    print(f"Filtro concluído: {len(transacoes_fora_do_horario)} transações não localizadas no WinThor.")
    return caminho_saida