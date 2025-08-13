import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.url_monitor import db, MonitoredURL
from src.models.synthetic_monitor import SyntheticTest
from src.routes.user import user_bp
from src.routes.monitor import monitor_bp
from src.routes.synthetic import synthetic_bp
## Alertas removidos a pedido do usuário
from src.scheduler import init_scheduler
import json

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
# Use SECRET_KEY from environment in production; fallback for local dev
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')

# Habilitar CORS
CORS(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(monitor_bp, url_prefix='/api')
app.register_blueprint(synthetic_bp, url_prefix='/api')

# Configuração do banco de dados
# Usar um caminho absoluto para o banco de dados
base_dir = os.path.abspath(os.path.dirname(__file__))
database_dir = os.path.join(base_dir, 'database')
os.makedirs(database_dir, exist_ok=True)

# Configurar o caminho do banco de dados com caminho absoluto
db_path = os.path.join(database_dir, 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
print(f"Usando banco de dados em: {db_path}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()
    
    # Adiciona URLs iniciais se não existirem
    initial_urls = [
        {'name': 'Mais Correios - Ofertas', 'url': 'https://www.maiscorreios.com.br/ofertas'},
        {'name': 'Mais Correios - Informática', 'url': 'https://www.maiscorreios.com.br/informatica'},
        {'name': 'Mais Correios - Eletrodomésticos', 'url': 'https://www.maiscorreios.com.br/eletrodomesticos'},
        {'name': 'Mais Correios - Celulares', 'url': 'https://www.maiscorreios.com.br/celulares-e-smartphones'},
        {'name': 'Mais Correios - Casa e Decoração', 'url': 'https://www.maiscorreios.com.br/casa-moveis-e-decoracao'},
        {'name': 'Mais Correios - Carrinho', 'url': 'https://www.maiscorreios.com.br/checkout/#/cart'}
    ]
    
    for url_data in initial_urls:
        existing = MonitoredURL.query.filter_by(url=url_data['url']).first()
        if not existing:
            new_url = MonitoredURL(url=url_data['url'], name=url_data['name'])
            db.session.add(new_url)
    
    # Adiciona teste sintético inicial se não existir (sem dados sensíveis)
    existing_test = SyntheticTest.query.filter_by(test_name='Fluxo de Compra - Mais Correios').first()
    if not existing_test:
        default_config = {
            'site_url': 'https://www.maiscorreios.com.br',
            'email': os.environ.get('SYNTHETIC_TEST_EMAIL', 'teste@exemplo.com'),
            'password': os.environ.get('SYNTHETIC_TEST_PASSWORD', 'senha123'),
            'product_name': 'envelope',
            'address': os.environ.get('SYNTHETIC_TEST_ADDRESS', 'Rua Exemplo, 123'),
            'payment_method': 'pix'
        }

        synthetic_test = SyntheticTest(
            test_name='Fluxo de Compra - Mais Correios',
            test_type='purchase_flow',
            site_url='https://www.maiscorreios.com.br',
            config_json=json.dumps(default_config)
        )
        db.session.add(synthetic_test)
    
    db.session.commit()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    # Inicializa os agendadores
    url_scheduler, synthetic_scheduler = init_scheduler(app)
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    finally:
        # Para os agendadores quando a aplicação é encerrada
        url_scheduler.stop()
        synthetic_scheduler.stop()
