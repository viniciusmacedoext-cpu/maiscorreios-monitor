import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_chrome_setup():
    print("🔍 Iniciando teste de configuração do Chrome...")
    
    # Verificar caminhos comuns do Chrome
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            print(f"✅ Chrome encontrado em: {path}")
            break
    
    if not chrome_path:
        print("❌ Google Chrome não encontrado nos caminhos padrão")
        return False
    
    try:
        print("🔧 Configurando ChromeDriver...")
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Não definir o caminho binário do Chrome, deixar o Selenium detectar automaticamente
        # chrome_options.binary_location = chrome_path
        
        # Instalar ChromeDriver automaticamente
        print("📥 Instalando ChromeDriver...")
        service = Service(ChromeDriverManager().install())
        
        print("🚀 Iniciando Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("🌐 Acessando site de teste...")
        driver.get("https://www.google.com")
        
        print(f"📋 Título da página: {driver.title}")
        
        driver.quit()
        print("✅ Teste concluído com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao configurar ou executar o Chrome: {e}")
        return False

if __name__ == "__main__":
    test_chrome_setup()