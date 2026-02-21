from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import json
import time

def capturar_token(url, user, password):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=new')
    options.add_argument('--log-level=3')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # --- OTIMIZAÇÕES EXTREMAS ---
    # 1. Não espera o carregamento de scripts externos/anúncios
    options.page_load_strategy = 'eager'
    # 2. Desativa TUDO que pesa: Imagens, Extensões e GPU
    options.add_argument('--blink-settings=imagesEnabled=false')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-software-rasterizer')
    # 3. Impede que o Chrome gaste tempo com som ou notificações
    options.add_argument('--mute-audio')
    
    options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
    servico = Service(ChromeDriverManager().install())
    
    try:
        driver = webdriver.Chrome(service=servico, options=options)
        driver.get(url)
        
        # Reduzimos o tempo de espera inicial (Angular costuma carregar os inputs rápido)
        time.sleep(1.2) 
        
        # Preenchimento direto
        driver.find_element(By.XPATH, '//*[@id="mat-input-0"]').send_keys(user)
        campo_senha = driver.find_element(By.XPATH, '//*[@id="mat-input-1"]')
        campo_senha.send_keys(password)
        campo_senha.send_keys(Keys.ENTER)

        token_extraido = None
        
        # Loop de alta frequência (verifica a rede a cada 0.1s para fechar na hora)
        for _ in range(60): 
            logs = driver.get_log('performance')
            for entry in logs:
                message = json.loads(entry['message'])['message']
                if message.get('method') == 'Network.requestWillBeSent':
                    headers = message.get('params', {}).get('request', {}).get('headers', {})
                    # Busca pelos headers que o seu CURL mostrou
                    auth = headers.get('Authorization') or headers.get('authorization') or headers.get('token')
                    
                    if auth and "eyJhbGci" in str(auth):
                        token_extraido = auth
                        break
            
            if token_extraido: break
            time.sleep(0.1) # Resposta quase instantânea

        driver.quit()
        
        if token_extraido:
            return str(token_extraido).replace("Bearer ", "").replace('"', '').strip()
        return None

    except:
        return None