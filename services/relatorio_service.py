import os
import json
import glob
from datetime import datetime

def gerar_relatorio_diario():
    hoje = datetime.now().strftime("%Y-%m-%d")
    
    # 1. Localizar os arquivos mais recentes do dia
    # Usamos glob para pegar o último arquivo gerado hoje em cada pasta
    try:
        arq_transacoes = sorted(glob.glob(f"transactions/transactions_{hoje}_*.json"))[-1]
        arq_pedidos = sorted(glob.glob(f"pedidos/pedidos_{hoje}_*.json"))[-1]
    except IndexError:
        print(f"Erro: Arquivos de hoje ({hoje}) não encontrados para cruzamento.")
        return None

    print(f"Cruzando dados: {arq_transacoes} + {arq_pedidos}")

    # 2. Carregar os dados
    with open(arq_transacoes, "r", encoding="utf-8") as f:
        data_trans = json.load(f)
    
    with open(arq_pedidos, "r", encoding="utf-8") as f:
        data_ped = json.load(f)

    # 3. Indexar pedidos por numPed para busca rápida (O(1))
    # Transformamos numPed em string para garantir a comparação correta
    mapa_pedidos = {str(p.get("numPed")): p for p in data_ped.get("content", [])}

    relatorio_final = {"transacoes": []}

    # 4. Comparar e Enriquecer
    for trans in data_trans.get("transacoes", []):
        codigo_maxima = str(trans.get("codigoPedidoMaxima", ""))
        
        # Busca o pedido correspondente no mapa
        pedido_correspondente = mapa_pedidos.get(codigo_maxima)

        # Prepara os dados de usuário e supervisor (extraídos do pedido)
        user_info = {"codigo": "", "nome": ""}
        super_info = {"codigo": "", "nome": ""}

        if pedido_correspondente:
            u_erp = pedido_correspondente.get("usuarioErp") or {}
            s_erp = pedido_correspondente.get("supervisor") or {}
            
            user_info = {
                "codigo": u_erp.get("codigo", ""),
                "nome": u_erp.get("nome", "")
            }
            super_info = {
                "codigo": s_erp.get("codigo", ""),
                "nome": s_erp.get("nome", "")
            }

        # Monta o objeto conforme sua estrutura solicitada
        item_relatorio = {
            "nomeFilial": trans.get("nomeFilial", ""),
            "nomeCliente": trans.get("nomeCliente", ""),
            "codigoPedidoMaxima": codigo_maxima,
            "valorPagamento": trans.get("valorPagamento", 0),
            "usuarioErp": user_info,
            "supervisor": super_info
        }
        
        relatorio_final["transacoes"].append(item_relatorio)

    # 5. Salvar o Relatório
    if not os.path.exists("relatorios"):
        os.makedirs("relatorios")

    caminho_relatorio = os.path.join("relatorios", f"relatorio_{hoje}.json")
    
    with open(caminho_relatorio, "w", encoding="utf-8") as f:
        json.dump(relatorio_final, f, indent=4, ensure_ascii=False)

    return caminho_relatorio