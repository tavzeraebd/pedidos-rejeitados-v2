import requests
import os
import json
import config
from datetime import datetime  # Adicionado para manipular datas
from dotenv import load_dotenv

def buscar_pedidos_importados_winthor():
    load_dotenv()
    token = os.getenv("WINTHOR_TOKEN")
    
    if not token:
        print("Erro: WINTHOR_TOKEN não encontrado no .env")
        return None

    url = config.URL_WINTHOR_IMPORTED 
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:147.0) Gecko/20100101 Firefox/147.0"
    }

    try:
        print(f"Consultando pedidos importados no WinThor ({url})...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"Erro API WinThor: {response.status_code}")
            return None
        
        dados_winthor = response.json()

        if not os.path.exists("winthor"):
            os.makedirs("winthor")

        # --- ALTERAÇÃO AQUI ---
        # Obtém a data atual no formato 2026-02-20
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        nome_arquivo = f"pedidos_winthor_{data_hoje}.json"
        caminho_completo = os.path.join("winthor", nome_arquivo)
        # ----------------------

        with open(caminho_completo, "w", encoding="utf-8") as f:
            json.dump(dados_winthor, f, indent=4, ensure_ascii=False)

        print(f"Sucesso! {len(dados_winthor)} pedidos salvos em: {nome_arquivo}")
        return caminho_completo

    except Exception as e:
        print(f"Falha crítica no serviço WinThor: {e}")
        return None