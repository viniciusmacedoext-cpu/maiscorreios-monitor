from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def inspect_product_page():
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
        # Navegar diretamente para uma página de produto conhecida
        product_url = "https://www.maiscorreios.com.br/fogao-4-bocas-dako-supreme-com-mesa-em-inox-e-acendimento-automatico-branco-%E2%80%93-bivolt-836908/p"
        print(f"=== NAVEGANDO PARA PRODUTO ===")
        print(f"URL: {product_url}")
        
        driver.get(product_url)
        time.sleep(5)
        
        print(f"Título: {driver.title}")
        print(f"URL atual: {driver.current_url}")
        
        print("\n=== PROCURANDO TODOS OS BOTÕES ===")
        buttons = driver.find_elements(By.TAG_NAME, "button")
        print(f"Encontrados {len(buttons)} botões")
        
        for i, btn in enumerate(buttons):
            text = btn.text.strip()
            btn_id = btn.get_attribute('id') or ''
            btn_class = btn.get_attribute('class') or ''
            btn_onclick = btn.get_attribute('onclick') or ''
            btn_type = btn.get_attribute('type') or ''
            
            if text or 'cart' in btn_class.lower() or 'cart' in btn_id.lower() or 'comprar' in text.lower() or 'adicionar' in text.lower():
                print(f"\nBotão {i+1}:")
                print(f"  Texto: '{text}'")
                print(f"  ID: '{btn_id}'")
                print(f"  Class: '{btn_class}'")
                print(f"  Type: '{btn_type}'")
                print(f"  OnClick: '{btn_onclick[:100]}'")
        
        print("\n=== PROCURANDO TODOS OS INPUTS ===")
        inputs = driver.find_elements(By.TAG_NAME, "input")
        print(f"Encontrados {len(inputs)} inputs")
        
        for i, inp in enumerate(inputs):
            inp_type = inp.get_attribute('type') or ''
            inp_value = inp.get_attribute('value') or ''
            inp_id = inp.get_attribute('id') or ''
            inp_class = inp.get_attribute('class') or ''
            
            if inp_type in ['submit', 'button'] or 'cart' in inp_class.lower() or 'cart' in inp_id.lower():
                print(f"\nInput {i+1}:")
                print(f"  Type: '{inp_type}'")
                print(f"  Value: '{inp_value}'")
                print(f"  ID: '{inp_id}'")
                print(f"  Class: '{inp_class}'")
        
        print("\n=== PROCURANDO LINKS QUE PODEM SER BOTÕES ===")
        links = driver.find_elements(By.TAG_NAME, "a")
        cart_links = []
        
        for link in links:
            text = link.text.strip().lower()
            href = link.get_attribute('href') or ''
            link_class = link.get_attribute('class') or ''
            
            if ('cart' in text or 'carrinho' in text or 'comprar' in text or 'adicionar' in text or
                'cart' in link_class.lower() or 'cart' in href.lower()):
                cart_links.append(link)
        
        print(f"Encontrados {len(cart_links)} links relacionados ao carrinho")
        for i, link in enumerate(cart_links):
            text = link.text.strip()
            href = link.get_attribute('href') or ''
            link_class = link.get_attribute('class') or ''
            print(f"\nLink {i+1}:")
            print(f"  Texto: '{text}'")
            print(f"  Href: '{href}'")
            print(f"  Class: '{link_class}'")
        
        print("\n=== PROCURANDO ELEMENTOS COM TEXTO RELACIONADO ===")
        # Procurar por qualquer elemento que contenha texto relacionado a compra
        all_elements = driver.find_elements(By.XPATH, "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'comprar') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'carrinho') or contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'adicionar')]")
        
        print(f"Encontrados {len(all_elements)} elementos com texto relacionado")
        for i, elem in enumerate(all_elements[:10]):  # Mostrar apenas os primeiros 10
            text = elem.text.strip()
            tag = elem.tag_name
            elem_class = elem.get_attribute('class') or ''
            elem_id = elem.get_attribute('id') or ''
            
            print(f"\nElemento {i+1}:")
            print(f"  Tag: {tag}")
            print(f"  Texto: '{text[:50]}'")
            print(f"  ID: '{elem_id}'")
            print(f"  Class: '{elem_class}'")
        
    except Exception as e:
        print(f"❌ ERRO: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_product_page()