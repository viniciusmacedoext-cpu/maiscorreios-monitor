import threading
import time
from datetime import datetime
from src.models.url_monitor import db, MonitoredURL, URLCheck
from src.routes.monitor import check_url_status
from src.models.synthetic_monitor import SyntheticTest
from src.routes.synthetic import execute_test_async

class URLMonitorScheduler:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.thread = None
        
    def start(self):
        """Inicia o agendador"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            print("✅ Agendador de monitoramento iniciado - verificações a cada 10 minutos")
    
    def stop(self):
        """Para o agendador"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("🛑 Agendador de monitoramento parado")
    
    def _run_scheduler(self):
        """Loop principal do agendador"""
        while self.running:
            try:
                self._check_all_urls()
                # Aguarda 10 minutos (600 segundos)
                for _ in range(600):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"❌ Erro no agendador: {e}")
                time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente
    
    def _check_all_urls(self):
        """Verifica todas as URLs ativas"""
        with self.app.app_context():
            try:
                urls = MonitoredURL.query.filter_by(is_active=True).all()
                print(f"🔍 Iniciando verificação de {len(urls)} URLs - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                for url in urls:
                    try:
                        check_result = check_url_status(url.url)
                        
                        new_check = URLCheck(
                            url_id=url.id,
                            status=check_result['status'],
                            response_time=check_result['response_time'],
                            status_code=check_result['status_code'],
                            error_message=check_result['error_message']
                        )
                        
                        db.session.add(new_check)

                        # (alertas removidos a pedido)
                        
                        # Log do resultado
                        status_icon = "✅" if check_result['status'] == 'online' else "❌"
                        response_time_str = f"({check_result['response_time']:.2f}s)" if check_result['response_time'] else ""
                        print(f"{status_icon} {url.name}: {check_result['status']} {response_time_str}")
                        
                    except Exception as e:
                        print(f"❌ Erro ao verificar {url.name}: {e}")
                
                db.session.commit()
                print(f"✅ Verificação concluída - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
            except Exception as e:
                print(f"❌ Erro na verificação geral: {e}")
                db.session.rollback()

class SyntheticTestScheduler:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.thread = None
        
    def start(self):
        """Inicia o agendador de testes sintéticos"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            print("✅ Agendador de testes sintéticos iniciado - execuções a cada 30 minutos")
    
    def stop(self):
        """Para o agendador"""
        self.running = False
        if self.thread:
            self.thread.join()
        print("🛑 Agendador de testes sintéticos parado")
    
    def _run_scheduler(self):
        """Loop principal do agendador"""
        while self.running:
            try:
                self._execute_all_tests()
                # Aguarda 30 minutos (1800 segundos)
                for _ in range(1800):
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                print(f"❌ Erro no agendador de testes sintéticos: {e}")
                time.sleep(60)  # Aguarda 1 minuto antes de tentar novamente
    
    def _execute_all_tests(self):
        """Executa todos os testes sintéticos ativos"""
        with self.app.app_context():
            try:
                tests = SyntheticTest.query.filter_by(is_active=True).all()
                print(f"🔍 Iniciando execução de {len(tests)} testes sintéticos - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                for test in tests:
                    try:
                        print(f"🔄 Executando teste: {test.test_name}")
                        execute_test_async(test.id, self.app)
                        # (alertas removidos a pedido)
                    except Exception as e:
                        print(f"❌ Erro ao executar teste {test.test_name}: {e}")
                
                print(f"✅ Execução de testes sintéticos iniciada - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
            except Exception as e:
                print(f"❌ Erro na execução geral de testes sintéticos: {e}")

def init_scheduler(app):
    """Inicializa os agendadores"""
    url_scheduler = URLMonitorScheduler(app)
    synthetic_scheduler = SyntheticTestScheduler(app)
    
    # Inicia ambos os agendadores
    url_scheduler.start()
    synthetic_scheduler.start()
    
    return url_scheduler, synthetic_scheduler

