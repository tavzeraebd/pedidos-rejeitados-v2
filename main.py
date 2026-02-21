import config
import os
from services.maxima_service import capturar_token
from services.transacoes_service import processar_e_salvar_transacoes
from services.pedidos_service import buscar_e_salvar_pedidos
from services.relatorio_service import gerar_relatorio_diario
from services.pedidos_winthor_service import buscar_pedidos_importados_winthor
# --- NOVO IMPORT ---
from services.filtro_importacao_service import verificar_pedidos_nao_importados

def atualizar_token_no_env(caminho_env, novo_token):
    """Atualiza apenas a variável MAXIMA_TOKEN sem apagar o restante do .env"""
    linhas = []
    if os.path.exists(caminho_env):
        with open(caminho_env, "r", encoding="utf-8") as f:
            linhas = f.readlines()

    token_atualizado = False
    novas_linhas = []
    
    for linha in linhas:
        if linha.strip().startswith("MAXIMA_TOKEN="):
            novas_linhas.append(f"MAXIMA_TOKEN={novo_token}\n")
            token_atualizado = True
        else:
            novas_linhas.append(linha)

    if not token_atualizado:
        if novas_linhas and not novas_linhas[-1].endswith("\n"):
            novas_linhas[-1] += "\n"
        novas_linhas.append(f"MAXIMA_TOKEN={novo_token}\n")

    with open(caminho_env, "w", encoding="utf-8") as f:
        f.writelines(novas_linhas)

def iniciar():
    # 1. Autenticação e Token
    token = capturar_token(config.URL_LOGIN, config.USUARIO, config.SENHA)
    
    if token:
        atualizar_token_no_env(config.ARQUIVO_ENV, token)
        print("Token Máxima atualizado no .env (demais variáveis preservadas).")
        
        # 2. Coleta de dados brutos da Máxima
        print("Coletando dados da Máxima...")
        processar_e_salvar_transacoes()
        buscar_e_salvar_pedidos()

        # 3. Geração do Relatório de Cruzamento (Máxima x Máxima)
        print("Gerando relatório de transações...")
        arq_relatorio = gerar_relatorio_diario()
        
        if arq_relatorio:
            print(f"Relatório gerado com sucesso.")
            
            # 4. Verificação no WinThor (Busca o que já foi importado)
            print("Iniciando verificação de importação no WinThor...")
            buscar_pedidos_importados_winthor()
            
            # --- NOVO PASSO 5: FILTRO PARA E-MAIL ---
            # Comparação final: Relatório vs WinThor
            print("Filtrando pedidos fora do horário (não importados)...")
            verificar_pedidos_nao_importados()
            
            print("--- PROCESSO FINALIZADO ---")
        else:
            print("Falha ao gerar o relatório. Verificação do WinThor abortada.")
            
    else:
        print("Erro ao capturar o token da Máxima.")

if __name__ == "__main__":
    iniciar()