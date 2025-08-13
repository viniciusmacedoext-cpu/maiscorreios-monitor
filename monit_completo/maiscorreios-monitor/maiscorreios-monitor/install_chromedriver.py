import os
import sys
import zipfile
import requests
import subprocess
from selenium import webdriver

def get_chrome_version():
    """Obtém a versão do Chrome instalado"""
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
    
    try:
        # Executar o Chrome com o argumento --version
        result = subprocess.run([chrome_path, '--version'], capture_output=True, text=True)
        version_output = result.stdout.strip()
        
        # Extrair a versão (formato: "Google Chrome XX.X.XXXX.XX")
        if version_output:
            version = version_output.split(' ')[2]
            print(f"📊 Versão do Chrome: {version}")
            return version
        else:
            print("❌ Não foi possível obter a versão do Chrome")
            return None
    except Exception as e:
        print(f"❌ Erro ao obter versão do Chrome: {e}")
        return None

def download_chromedriver(version):
    """Baixa o ChromeDriver compatível com a versão do Chrome"""
    try:
        # Obter a versão principal do Chrome (ex: 91 de 91.0.4472.124)
        major_version = version.split('.')[0]
        
        # URL base para download do ChromeDriver
        base_url = f"https://chromedriver.storage.googleapis.com/LATEST_RELEASE_{major_version}"
        
        # Obter a versão exata do ChromeDriver
        response = requests.get(base_url)
        if response.status_code != 200:
            print(f"❌ Erro ao obter versão do ChromeDriver: {response.status_code}")
            return False
        
        chromedriver_version = response.text.strip()
        print(f"📊 Versão do ChromeDriver: {chromedriver_version}")
        
        # URL para download do ChromeDriver
        download_url = f"https://chromedriver.storage.googleapis.com/{chromedriver_version}/chromedriver_win32.zip"
        
        # Diretório para salvar o ChromeDriver
        driver_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'drivers')
        os.makedirs(driver_dir, exist_ok=True)
        
        # Baixar o arquivo zip
        print(f"📥 Baixando ChromeDriver de {download_url}...")
        response = requests.get(download_url)
        if response.status_code != 200:
            print(f"❌ Erro ao baixar ChromeDriver: {response.status_code}")
            return False
        
        # Salvar o arquivo zip
        zip_path = os.path.join(driver_dir, 'chromedriver.zip')
        with open(zip_path, 'wb') as f:
            f.write(response.content)
        
        # Extrair o arquivo zip
        print(f"📦 Extraindo ChromeDriver para {driver_dir}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(driver_dir)
        
        # Caminho para o executável do ChromeDriver
        chromedriver_path = os.path.join(driver_dir, 'chromedriver.exe')
        
        # Verificar se o arquivo existe
        if os.path.exists(chromedriver_path):
            print(f"✅ ChromeDriver instalado em: {chromedriver_path}")
            return chromedriver_path
        else:
            print("❌ ChromeDriver não encontrado após extração")
            return False
    except Exception as e:
        print(f"❌ Erro ao baixar ChromeDriver: {e}")
        return False

def test_chromedriver(chromedriver_path):
    """Testa se o ChromeDriver está funcionando corretamente"""
    try:
        print("🔧 Configurando ChromeDriver...")
        
        # Configurar o caminho do ChromeDriver
        os.environ["webdriver.chrome.driver"] = chromedriver_path
        
        # Configurar opções do Chrome
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        
        # Iniciar o Chrome
        print("🚀 Iniciando Chrome...")
        driver = webdriver.Chrome(executable_path=chromedriver_path, options=chrome_options)
        
        # Acessar um site de teste
        print("🌐 Acessando site de teste...")
        driver.get("https://www.google.com")
        
        # Verificar se o site foi carregado
        print(f"📋 Título da página: {driver.title}")
        
        # Fechar o Chrome
        driver.quit()
        
        print("✅ Teste concluído com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao testar ChromeDriver: {e}")
        return False

def main():
    print("🔍 Iniciando instalação do ChromeDriver...")
    
    # Obter a versão do Chrome
    chrome_version = get_chrome_version()
    if not chrome_version:
        print("❌ Não foi possível continuar sem a versão do Chrome")
        return False
    
    # Baixar o ChromeDriver
    chromedriver_path = download_chromedriver(chrome_version)
    if not chromedriver_path:
        print("❌ Não foi possível baixar o ChromeDriver")
        return False
    
    # Testar o ChromeDriver
    if test_chromedriver(chromedriver_path):
        print("\n✅✅✅ ChromeDriver instalado e testado com sucesso!")
        print(f"📂 Caminho do ChromeDriver: {chromedriver_path}")
        print("\nPara usar o ChromeDriver no seu código, adicione o seguinte:")
        print(f"\nos.environ['webdriver.chrome.driver'] = '{chromedriver_path}'")
        print("driver = webdriver.Chrome(executable_path='{chromedriver_path}', options=chrome_options)")
        return True
    else:
        print("\n❌❌❌ Falha ao testar o ChromeDriver")
        return False

if __name__ == "__main__":
    main()