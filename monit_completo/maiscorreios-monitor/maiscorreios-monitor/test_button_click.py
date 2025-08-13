from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

def test_button_click():
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
        
        print("\n=== TESTANDO DIFERENTES MÉTODOS DE CLIQUE ===")
        
        # Método 1: Encontrar pelo span e depois o botão pai
        try:
            print("\nMétodo 1: Encontrar pelo span")
            span_element = driver.find_element(By.CSS_SELECTOR, ".vtex-add-to-cart-button-0-x-buttonText")
            if span_element:
                print(f"Span encontrado: {span_element.text}")
                button = span_element.find_element(By.XPATH, "./ancestor::button[1]")
                print(f"Botão pai encontrado")
                
                # Verificar se o botão está visível e habilitado
                print(f"Botão visível: {button.is_displayed()}")
                print(f"Botão habilitado: {button.is_enabled()}")
                
                # Scroll para o elemento
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)
                
                # Tentar clique normal
                try:
                    button.click()
                    print("✅ Clique normal funcionou")
                    time.sleep(2)
                    return True
                except Exception as e:
                    print(f"❌ Clique normal falhou: {e}")
                
                # Tentar clique com JavaScript
                try:
                    driver.execute_script("arguments[0].click();", button)
                    print("✅ Clique com JavaScript funcionou")
                    time.sleep(2)
                    return True
                except Exception as e:
                    print(f"❌ Clique com JavaScript falhou: {e}")
                
                # Tentar clique com ActionChains
                try:
                    actions = ActionChains(driver)
                    actions.move_to_element(button).click().perform()
                    print("✅ Clique com ActionChains funcionou")
                    time.sleep(2)
                    return True
                except Exception as e:
                    print(f"❌ Clique com ActionChains falhou: {e}")
                    
        except Exception as e:
            print(f"❌ Método 1 falhou: {e}")
        
        # Método 2: Procurar botão diretamente
        try:
            print("\nMétodo 2: Procurar botão diretamente")
            buttons = driver.find_elements(By.CSS_SELECTOR, "button[class*='bg-action-primary']")
            print(f"Encontrados {len(buttons)} botões com bg-action-primary")
            
            for i, btn in enumerate(buttons):
                text = btn.text.strip()
                print(f"Botão {i+1}: '{text}'")
                
                if 'adicionar' in text.lower() or 'carrinho' in text.lower():
                    print(f"Tentando clicar no botão: '{text}'")
                    
                    # Scroll para o elemento
                    driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                    time.sleep(1)
                    
                    try:
                        driver.execute_script("arguments[0].click();", btn)
                        print("✅ Clique com JavaScript funcionou")
                        time.sleep(2)
                        return True
                    except Exception as e:
                        print(f"❌ Clique falhou: {e}")
                        
        except Exception as e:
            print(f"❌ Método 2 falhou: {e}")
        
        # Método 3: XPath com texto
        try:
            print("\nMétodo 3: XPath com texto")
            xpath = "//button[.//span[contains(text(), 'Adicionar ao carrinho')]]"
            button = driver.find_element(By.XPATH, xpath)
            
            if button:
                print("Botão encontrado via XPath")
                print(f"Botão visível: {button.is_displayed()}")
                print(f"Botão habilitado: {button.is_enabled()}")
                
                # Scroll para o elemento
                driver.execute_script("arguments[0].scrollIntoView(true);", button)
                time.sleep(1)
                
                try:
                    driver.execute_script("arguments[0].click();", button)
                    print("✅ Clique com JavaScript funcionou")
                    time.sleep(2)
                    return True
                except Exception as e:
                    print(f"❌ Clique falhou: {e}")
                    
        except Exception as e:
            print(f"❌ Método 3 falhou: {e}")
        
        print("\n❌ TODOS OS MÉTODOS FALHARAM")
        return False
        
    except Exception as e:
        print(f"❌ ERRO GERAL: {e}")
        return False
    
    finally:
        driver.quit()

if __name__ == "__main__":
    success = test_button_click()
    if success:
        print("\n🎉 TESTE DE CLIQUE BEM-SUCEDIDO!")
    else:
        print("\n💥 TESTE DE CLIQUE FALHOU!")