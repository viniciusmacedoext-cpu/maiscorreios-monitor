import os
import sys
import logging
from src.synthetic_engine import MaisCorreiosSyntheticEngine

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_synthetic_engine():
    print("🔍 Testando o motor de testes sintéticos...")
    
    # Verificar se o Chrome está instalado
    chrome_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    ]
    
    chrome_found = False
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_found = True
            print(f"✅ Chrome encontrado em: {path}")
            break
    
    if not chrome_found:
        print("❌ Google Chrome não encontrado nos caminhos padrão")
        return False
    
    # Verificar se o ChromeDriver está disponível
    drivers_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drivers')
    chromedriver_path = os.path.join(drivers_dir, 'chromedriver.exe')
    
    if not os.path.exists(chromedriver_path):
        print(f"❌ ChromeDriver não encontrado em: {chromedriver_path}")
        print("Execute o script download_chromedriver.py para baixar o ChromeDriver")
        return False
    
    print(f"✅ ChromeDriver encontrado em: {chromedriver_path}")
    
    # Inicializar o motor de testes
    engine = MaisCorreiosSyntheticEngine(headless=False, timeout=30)
    
    try:
        # Testar configuração do driver
        print("🔧 Testando configuração do driver...")
        if not engine.setup_driver():
            print("❌ Falha ao configurar driver")
            return False
        
        # Testar navegação para um site simples
        print("🌐 Testando navegação para google.com...")
        if not engine.navigate_to("https://www.google.com"):
            print("❌ Falha ao navegar para google.com")
            return False
        
        # Tirar screenshot
        screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_screenshot.png')
        if engine.take_screenshot(screenshot_path):
            print(f"📸 Screenshot salvo em: {screenshot_path}")
        
        print("✅ Teste de navegação concluído com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        return False
    finally:
        # Limpar recursos
        if engine:
            engine.cleanup()

if __name__ == "__main__":
    success = test_synthetic_engine()
    if success:
        print("\n✅✅✅ Todos os testes concluídos com sucesso!")
        sys.exit(0)
    else:
        print("\n❌❌❌ Falha nos testes!")
        sys.exit(1)