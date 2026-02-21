import requests
import os
import json
from datetime import datetime
from dotenv import load_dotenv

def buscar_e_salvar_pedidos():
    load_dotenv()
    token = os.getenv("MAXIMA_TOKEN")
    
    if not token:
        print("Erro: Token não encontrado no .env")
        return None

    # Configuração de Datas
    hoje = datetime.now().strftime("%Y-%m-%d")
    data_inicio = f"{hoje}T00:00:00.000Z"
    data_fim = f"{hoje}T23:59:59.999Z"

    url = "https://centralapi.solucoesmaxima.com.br/api/v1/pedido/pesquisar"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0"
    }

    todos_os_pedidos = []
    pagina_atual = 0
    tamanho_pagina = 1000  # Otimização: Buscando de 1000 em 1000

    try:
        while True:
            payload = {
                "dataInicio": data_inicio,
                "dataFim": data_fim,
                "listaCodSuperv": [],
                "listaCodUsur": [], 
                "listaStatus": [],
                "listaTiposPedidos": [],
                "size": tamanho_pagina,
                "page": pagina_atual
            }

            # Log para acompanhar o progresso no console
            print(f"Buscando bloco {pagina_atual + 1} ({tamanho_pagina} itens)...")
            
            # Aumentamos o timeout para 30s pois o servidor demora mais para processar 1000 itens
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"Erro na requisição: {response.status_code}")
                break
            
            dados = response.json()
            pedidos_da_pagina = dados.get("content", [])
            total_geral = dados.get("totalElements", 0)

            if not pedidos_da_pagina:
                break
            
            todos_os_pedidos.extend(pedidos_da_pagina)
            
            print(f"Progresso: {len(todos_os_pedidos)} / {total_geral}")

            # Condição de parada: se já pegamos tudo ou se o que veio é menor que o que pedimos
            if len(todos_os_pedidos) >= total_geral or len(pedidos_da_pagina) < tamanho_pagina:
                break
                
            pagina_atual += 1

        # Estrutura final
        resultado_final = {
            "content": todos_os_pedidos,
            "totalElements": len(todos_os_pedidos)
        }

        # Salvamento
        if not os.path.exists("pedidos"):
            os.makedirs("pedidos")

        nome_arquivo = datetime.now().strftime("pedidos_%Y-%m-%d_%H-%M-%S.json")
        caminho_completo = os.path.join("pedidos", nome_arquivo)

        with open(caminho_completo, "w", encoding="utf-8") as f:
            json.dump(resultado_final, f, indent=4, ensure_ascii=False)

        print(f"Concluído! {len(todos_os_pedidos)} pedidos salvos com sucesso.")
        return caminho_completo

    except Exception as e:
        print(f"Falha crítica no serviço de pedidos: {e}")
        return None