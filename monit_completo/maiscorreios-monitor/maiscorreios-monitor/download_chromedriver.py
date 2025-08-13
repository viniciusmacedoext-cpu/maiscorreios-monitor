import os
import sys
import zipfile
import requests
import subprocess
from io import BytesIO

def get_chrome_version():
    """Obtém a versão principal do Chrome instalado"""
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
        return None
    
    # Retorna a versão principal do Chrome
    return "139"

def main():
    print("🔍 Baixando ChromeDriver compatível...")
    
    # Obter a versão do Chrome
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("❌ Não foi possível determinar a versão do Chrome")
        return False
    
    print(f"📊 Versão do Chrome detectada: {chrome_version}")
    
    # Para o Chrome 139, vamos usar a versão 139 do ChromeDriver
    # que é compatível com o Chrome 139
    chromedriver_version = "139.0.7258.66"
    print(f"📊 Usando ChromeDriver versão: {chromedriver_version}")
    
    # Diretório para salvar o ChromeDriver
    driver_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drivers')
    os.makedirs(driver_dir, exist_ok=True)
    
    try:
        # URL para download do ChromeDriver do Chrome for Testing
        download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{chromedriver_version}/win32/chromedriver-win32.zip"
        
        # Baixar o arquivo zip
        print(f"📥 Baixando ChromeDriver de {download_url}...")
        response = requests.get(download_url)
        if response.status_code != 200:
            print(f"❌ Erro ao baixar ChromeDriver: {response.status_code}")
            return False
        
        # Extrair o arquivo zip diretamente da memória
        print(f"📦 Extraindo ChromeDriver para {driver_dir}...")
        with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
            zip_ref.extractall(driver_dir)
        
        # Caminho para o executável do ChromeDriver na pasta extraída
        extracted_chromedriver_path = os.path.join(driver_dir, 'chromedriver-win32', 'chromedriver.exe')
        
        # Caminho de destino para o executável do ChromeDriver
        chromedriver_path = os.path.join(driver_dir, 'chromedriver.exe')
        
        # Copiar o arquivo para o diretório drivers
        if os.path.exists(extracted_chromedriver_path):
            import shutil
            shutil.copy2(extracted_chromedriver_path, chromedriver_path)
            print(f"✅ ChromeDriver copiado de {extracted_chromedriver_path} para {chromedriver_path}")
        
        # Verificar se o arquivo existe
        if os.path.exists(chromedriver_path):
            print(f"✅ ChromeDriver instalado em: {chromedriver_path}")
            print("\n✅✅✅ ChromeDriver baixado com sucesso!")
            print(f"📂 Caminho do ChromeDriver: {chromedriver_path}")
            print("\nAdicione este diretório ao PATH do sistema ou use o caminho completo no código.")
            return True
        else:
            print("❌ ChromeDriver não encontrado após extração")
            return False
    except Exception as e:
        print(f"❌ Erro ao baixar ChromeDriver: {e}")
        return False

if __name__ == "__main__":
    main()