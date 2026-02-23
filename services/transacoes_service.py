import requests
import os
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

def processar_e_salvar_transacoes():
    load_dotenv()
    token = os.getenv("MAXIMA_TOKEN")
    if not token:
        print("Erro: Token não encontrado no .env")
        return None

    # OTIMIZAÇÃO DE DATA: 
    # Usamos apenas a data (YYYY-MM-DD). Algumas APIs da Máxima ignoram o T03:00... 
    # se o filtro for por dia cheio. Vamos garantir o formato do seu CURL.
    hoje = datetime.now().strftime("%Y-%m-%d")
    data_inicio = f"{hoje}T00:00:00.000Z"
    data_fim = f"{hoje}T23:59:59.000Z"

    url = "https://maxpayment-api.solucoesmaxima.com.br/relatorio/ConsultarPagamentoPorPeriodo"
    
    # Ajustamos os parâmetros para garantir que a paginação e o filtro de status capturem tudo
    params = {
        "Pagina": 1,
        "ItensPorPagina": 50, # Aumentado para garantir que pegamos todas do dia
        "CampoOrdem": "dtIncluido",
        "TipoOrdemAsc": "false",
        "dataInicio": data_inicio,
        "dataFim": data_fim,
        "filialId": 0,
        "statusPagamento": 0,
        "ambiente": -1,
        "paginar": "true",
        "gateways": 3,
        "statusPagamentos": 5 # Filtro de Pré-autorizados (conforme seu CURL)
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0",
        "Origin": "https://maxpayment.solucoesmaxima.com.br",
        "Referer": "https://maxpayment.solucoesmaxima.com.br/"
    }

    try:
        # Debug: Mostrar a URL que está sendo chamada (opcional)
        # print(f"Chamando API para o dia: {hoje}")

        response = requests.get(url, params=params, headers=headers, timeout=20)
        
        if response.status_code != 200:
            print(f"Erro API: {response.status_code} - {response.text}")
            return None
        
        dados_originais = response.json()
        
        # A API da Máxima às vezes retorna os dados dentro de 'data' ou 'itens'
        # Baseado no seu exemplo, é 'data'
        lista_data = dados_originais.get("data", [])

        if not lista_data:
            print(f"Nenhuma transação localizada para o dia {hoje}. Processo encerrado.")
            return None

        transacoes_formatadas = []
        for item in lista_data:
            # Acessamos o objeto 'pedido' interno
            pedido_obj = item.get("pedido") or {}
            
            nova_transacao = {
                "nomeFilial": str(item.get("nomeFilial", ""))[:2],
                "nomeCliente": item.get("nomeCliente", ""),
                "codigoPedidoMaxima": str(pedido_obj.get("codigoPedidoMaxima", "")),
                "valorPagamento": item.get("valorPagamento", 0)
            }
            transacoes_formatadas.append(nova_transacao)

        # Salvamento
        resultado_final = {"transacoes": transacoes_formatadas}
        
        if not os.path.exists("transactions"):
            os.makedirs("transactions")

        agora = datetime.now()
        nome_arquivo = agora.strftime("transactions_%Y-%m-%d_%H-%M-%S.json")
        caminho_completo = os.path.join("transactions", nome_arquivo)

        with open(caminho_completo, "w", encoding="utf-8") as f:
            json.dump(resultado_final, f, indent=4, ensure_ascii=False)

        return caminho_completo

    except Exception as e:
        print(f"Falha crítica no serviço de pedidos: {e}")
        return None