from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def inspect_maiscorreios():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = webdriver.Chrome(options=options)
    
    try:
        print("Acessando o site...")
        driver.get('https://www.maiscorreios.com.br')
        time.sleep(10)  # Aguardar mais tempo para carregamento completo
        
        print(f"Título: {driver.title}")
        print(f"URL: {driver.current_url}")
        
        # Verificar se há redirecionamentos ou mudanças na URL
        print(f"URL final após carregamento: {driver.current_url}")
        
        # Obter todo o HTML da página para análise
        print("\n=== ESTRUTURA GERAL DA PÁGINA ===")
        page_source = driver.page_source
        print(f"Tamanho do HTML: {len(page_source)} caracteres")
        
        # Procurar por elementos de navegação
        print("\n=== ELEMENTOS DE NAVEGAÇÃO ===")
        nav_elements = driver.find_elements(By.TAG_NAME, 'nav')
        print(f"Encontrados {len(nav_elements)} elementos <nav>")
        
        # Procurar por menus
        menu_selectors = ['.menu', '.navigation', '.navbar', '.header-menu', '.main-menu']
        for selector in menu_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"Encontrados {len(elements)} elementos com seletor: {selector}")
            except:
                pass
        
        # Procurar por todos os links da página
        print("\n=== TODOS OS LINKS ===")
        all_links = driver.find_elements(By.TAG_NAME, 'a')
        print(f"Total de links encontrados: {len(all_links)}")
        
        # Categorizar links
        category_links = []
        product_links = []
        other_links = []
        
        for link in all_links:
            href = link.get_attribute('href') or ''
            text = link.text.strip()
            
            if any(word in href.lower() for word in ['categoria', 'category', 'departamento']):
                category_links.append((href, text))
            elif any(word in href.lower() for word in ['produto', 'product', 'item']):
                product_links.append((href, text))
            elif href and text:
                other_links.append((href, text))
        
        print(f"Links de categoria: {len(category_links)}")
        for href, text in category_links[:10]:  # Primeiros 10
            print(f"  {text} -> {href}")
        
        print(f"\nLinks de produto: {len(product_links)}")
        for href, text in product_links[:10]:  # Primeiros 10
            print(f"  {text} -> {href}")
        
        print(f"\nOutros links importantes: {len(other_links)}")
        for href, text in other_links[:15]:  # Primeiros 15
            if text and len(text) > 2:  # Apenas links com texto significativo
                print(f"  {text} -> {href}")
        
        # Procurar por formulários
        print("\n=== FORMULÁRIOS ===")
        forms = driver.find_elements(By.TAG_NAME, 'form')
        print(f"Encontrados {len(forms)} formulários")
        
        for i, form in enumerate(forms):
            action = form.get_attribute('action') or ''
            method = form.get_attribute('method') or 'GET'
            print(f"Formulário {i+1}: Action={action}, Method={method}")
            
            # Inputs dentro do formulário
            form_inputs = form.find_elements(By.TAG_NAME, 'input')
            for j, input_elem in enumerate(form_inputs):
                input_type = input_elem.get_attribute('type') or 'text'
                placeholder = input_elem.get_attribute('placeholder') or ''
                name = input_elem.get_attribute('name') or ''
                print(f"  Input {j+1}: Type={input_type}, Name={name}, Placeholder={placeholder}")
        
        # Procurar por elementos com texto relacionado a busca
        print("\n=== ELEMENTOS COM TEXTO DE BUSCA ===")
        search_texts = ['buscar', 'pesquisar', 'procurar', 'search', 'find']
        for text in search_texts:
            try:
                elements = driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text}')]")
                if elements:
                    print(f"Encontrados {len(elements)} elementos com texto '{text}'")
                    for elem in elements[:3]:  # Primeiros 3
                        print(f"  Tag: {elem.tag_name}, Text: {elem.text[:50]}")
            except:
                pass
        
        # Verificar se há JavaScript que pode estar carregando conteúdo dinamicamente
        print("\n=== SCRIPTS ===")
        scripts = driver.find_elements(By.TAG_NAME, 'script')
        print(f"Encontrados {len(scripts)} elementos <script>")
        
        # Aguardar mais tempo e verificar novamente
        print("\n=== AGUARDANDO CARREGAMENTO ADICIONAL ===")
        time.sleep(10)
        
        # Verificar novamente após aguardar
        new_inputs = driver.find_elements(By.TAG_NAME, 'input')
        print(f"Inputs após aguardar: {len(new_inputs)}")
        
        new_links = driver.find_elements(By.TAG_NAME, 'a')
        print(f"Links após aguardar: {len(new_links)}")
        
    except Exception as e:
        print(f"Erro geral: {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_maiscorreios()