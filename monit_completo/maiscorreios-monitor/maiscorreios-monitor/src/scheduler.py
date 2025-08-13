import threading
import time
from datetime import datetime
from src.models.url_monitor import MonitoredURL, URLCheck, db
from src.models.synthetic_monitor import SyntheticTest, SyntheticTestResult, SyntheticTestStep
from src.routes.monitor import check_url_status
from src.routes.synthetic import execute_test_async
from src.utils.timezone import format_brazil_time

class URLMonitorScheduler:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.thread = None
        
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print(f"🔄 Scheduler de URLs iniciado - {format_brazil_time()}")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            print(f"⏹️ Scheduler de URLs parado - {format_brazil_time()}")
    
    def _run(self):
        while self.running:
            try:
                with self.app.app_context():
                    self._check_all_urls()
                time.sleep(600)  # 10 minutos (aumentado de 5 para 10)
            except Exception as e:
                print(f"❌ Erro no scheduler de URLs: {e} - {format_brazil_time()}")
                time.sleep(120)  # 2 minutos em caso de erro (aumentado de 1 para 2)
    
    def _check_all_urls(self):
        urls = MonitoredURL.query.filter_by(is_active=True).all()
        if not urls:
            return
        
        print(f"🔍 Iniciando verificação de {len(urls)} URLs - {format_brazil_time()}")
        
        for url in urls:
            try:
                status, response_time, status_code, error_message = check_url_status(url.url)
                
                check = URLCheck(
                    url_id=url.id,
                    status=status,
                    response_time=response_time,
                    status_code=status_code,
                    error_message=error_message
                )
                
                db.session.add(check)
                db.session.commit()
                
                print(f"✅ {url.name}: {status} ({response_time:.2f}s) - {format_brazil_time()}")
                
            except Exception as e:
                print(f"❌ Erro ao verificar {url.name}: {e} - {format_brazil_time()}")
                continue
        
        print(f"✅ Verificação concluída - {format_brazil_time()}")

class SyntheticTestScheduler:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.thread = None
        
    def start(self):
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
            print(f"🔄 Scheduler de testes sintéticos iniciado - {format_brazil_time()}")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            print(f"⏹️ Scheduler de testes sintéticos parado - {format_brazil_time()}")
    
    def _run(self):
        while self.running:
            try:
                with self.app.app_context():
                    self._execute_all_tests()
                time.sleep(3600)  # 1 hora (aumentado de 30 minutos para 1 hora)
            except Exception as e:
                print(f"❌ Erro no scheduler de testes sintéticos: {e} - {format_brazil_time()}")
                time.sleep(600)  # 10 minutos em caso de erro (aumentado de 5 para 10)
    
    def _execute_all_tests(self):
        tests = SyntheticTest.query.filter_by(is_active=True).all()
        if not tests:
            return
        
        print(f"🔍 Iniciando execução de {len(tests)} testes sintéticos - {format_brazil_time()}")
        
        for test in tests:
            try:
                execute_test_async(test.id, self.app)
                print(f"✅ Teste {test.test_name} iniciado - {format_brazil_time()}")
            except Exception as e:
                print(f"❌ Erro ao executar teste {test.test_name}: {e} - {format_brazil_time()}")
                continue
        
        print(f"✅ Execução de testes sintéticos iniciada - {format_brazil_time()}")

def init_scheduler(app):
    url_scheduler = URLMonitorScheduler(app)
    synthetic_scheduler = SyntheticTestScheduler(app)
    
    url_scheduler.start()
    synthetic_scheduler.start()
    
    return url_scheduler, synthetic_scheduler

