from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def debug_product_navigation():
    # Configurar Chrome
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("=== NAVEGANDO PARA O SITE ===")
        driver.get('https://www.maiscorreios.com.br')
        print(f"Título: {driver.title}")
        print(f"URL atual: {driver.current_url}")
        
        # Aguardar carregamento
        time.sleep(5)
        
        print("\n=== PROCURANDO LINKS DE PRODUTOS ===")
        product_link_selectors = [
            "a[href*='/p']",  # Links que terminam com /p (padrão do site)
            "a[href*='produto']",
            "a[href*='item']",
            "a[href*='fogao']",
            "a[href*='geladeira']",
            "a[href*='microondas']"
        ]
        
        product_link = None
        for selector in product_link_selectors:
            print(f"\nTestando seletor: {selector}")
            links = driver.find_elements(By.CSS_SELECTOR, selector)
            print(f"Encontrados {len(links)} links")
            
            if links:
                for i, link in enumerate(links[:5]):  # Mostrar apenas os primeiros 5
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()[:50]  # Primeiros 50 caracteres
                    print(f"  Link {i+1}: {href} - Texto: '{text}'")
                    
                    # Filtrar apenas links que são realmente produtos
                    if ('/p' in href and 'maiscorreios.com.br' in href and 
                        'politica' not in href.lower() and 
                        'privacidade' not in href.lower() and 
                        'termo' not in href.lower() and
                        href.endswith('/p')):
                        product_link = link
                        print(f"  ✅ PRODUTO VÁLIDO ENCONTRADO: {href}")
                        break
                        
                if product_link:
                    break
        
        if not product_link:
            print("\n❌ NENHUM LINK DE PRODUTO VÁLIDO ENCONTRADO")
            return
        
        print(f"\n=== CLICANDO NO PRODUTO ===")
        print(f"Link selecionado: {product_link.get_attribute('href')}")
        
        # Tentar clicar
        try:
            driver.execute_script("arguments[0].click();", product_link)
            print("✅ Clique executado com JavaScript")
        except Exception as e:
            print(f"❌ Erro ao clicar: {e}")
            return
        
        # Aguardar navegação
        time.sleep(5)
        
        print(f"\n=== VERIFICANDO RESULTADO ===")
        current_url = driver.current_url
        print(f"URL após clique: {current_url}")
        print(f"Título da página: {driver.title}")
        
        if '/p' in current_url:
            print("✅ SUCESSO: Estamos em uma página de produto")
        else:
            print("❌ FALHA: Não estamos em uma página de produto")
            
        # Verificar se há botão de adicionar ao carrinho
        print("\n=== PROCURANDO BOTÃO ADICIONAR AO CARRINHO ===")
        add_to_cart_selectors = [
            "button#product-addtocart-button",
            "button[title*='Adicionar']",
            "button[title*='Carrinho']",
            ".btn-cart",
            "input[type='submit'][value*='Adicionar']",
            "button.addtocart",
            "a.btn-cart",
            "button[onclick*='cart']"
        ]
        
        for selector in add_to_cart_selectors:
            buttons = driver.find_elements(By.CSS_SELECTOR, selector)
            if buttons:
                print(f"✅ Encontrado botão com seletor '{selector}': {len(buttons)} elemento(s)")
                for i, btn in enumerate(buttons[:3]):
                    text = btn.text.strip()[:30]
                    print(f"  Botão {i+1}: '{text}'")
            else:
                print(f"❌ Nenhum botão encontrado com seletor '{selector}'")
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_product_navigation()