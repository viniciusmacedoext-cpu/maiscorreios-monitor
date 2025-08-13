import threading
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from src.models.synthetic_monitor import db, SyntheticTest, SyntheticTestResult, SyntheticTestStep
from src.synthetic_engine import MaisCorreiosSyntheticEngine
from src.utils.timezone import get_brazil_datetime_for_db

synthetic_bp = Blueprint('synthetic', __name__)

def execute_test_async(test_id, app=None):
    """Executa um teste sintético de forma assíncrona"""
    def run_test():
        with app.app_context():
            try:
                test = SyntheticTest.query.get(test_id)
                if not test:
                    print(f"❌ Teste {test_id} não encontrado")
                    return
                
                print(f"🔄 Iniciando teste: {test.test_name}")
                
                # Configuração do teste
                config = {
                    'site_url': test.site_url,
                    'email': test.email,
                    'password': test.password,
                    'product_name': test.product_name,
                    'address': test.address,
                    'payment_method': test.payment_method,
                    'headless': test.headless
                }
                
                # Executa o teste
                engine = MaisCorreiosSyntheticEngine(headless=config['headless'])
                result = engine.execute_full_test(config)
                
                # Salva o resultado
                test_result = SyntheticTestResult(
                    test_id=test.id,
                    status=result['status'],
                    steps_completed=result['steps_completed'],
                    total_steps=result['total_steps'],
                    duration=result['duration'],
                    error_message=result.get('error_message')
                )
                
                db.session.add(test_result)
                db.session.commit()
                
                # Salva os passos individuais
                for step_data in result.get('steps', []):
                    step = SyntheticTestStep(
                        result_id=test_result.id,
                        step_number=step_data['step_number'],
                        step_name=step_data['step_name'],
                        status=step_data['status'],
                        duration=step_data.get('duration'),
                        error_message=step_data.get('error_message')
                    )
                    db.session.add(step)
                
                db.session.commit()
                
                print(f"✅ Teste {test.test_name} concluído: {result['status']}")
                
            except Exception as e:
                print(f"❌ Erro no teste {test_id}: {e}")
                
                # Salva erro no banco
                try:
                    test = SyntheticTest.query.get(test_id)
                    if test:
                        error_result = SyntheticTestResult(
                            test_id=test.id,
                            status='error',
                            steps_completed=0,
                            total_steps=8,
                            duration=0,
                            error_message=str(e)
                        )
                        db.session.add(error_result)
                        db.session.commit()
                except:
                    pass
    
    # Executa em thread separada
    thread = threading.Thread(target=run_test, daemon=True)
    thread.start()

@synthetic_bp.route('/synthetic-tests', methods=['GET'])
def get_synthetic_tests():
    """Lista todos os testes sintéticos"""
    tests = SyntheticTest.query.all()
    return jsonify([test.to_dict() for test in tests])

@synthetic_bp.route('/synthetic-tests', methods=['POST'])
def add_synthetic_test():
    """Adiciona um novo teste sintético"""
    data = request.get_json()
    
    required_fields = ['test_name', 'site_url', 'email', 'password', 'product_name', 'address', 'payment_method']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'Campo {field} é obrigatório'}), 400
    
    # Verifica se já existe um teste com o mesmo nome
    existing_test = SyntheticTest.query.filter_by(test_name=data['test_name']).first()
    if existing_test:
        return jsonify({'error': 'Já existe um teste com este nome'}), 400
    
    # Cria novo teste
    new_test = SyntheticTest(
        test_name=data['test_name'],
        site_url=data['site_url'],
        email=data['email'],
        password=data['password'],
        product_name=data['product_name'],
        address=data['address'],
        payment_method=data['payment_method'],
        headless=data.get('headless', True)
    )
    
    db.session.add(new_test)
    db.session.commit()
    
    return jsonify(new_test.to_dict()), 201

@synthetic_bp.route('/synthetic-tests/<int:test_id>', methods=['PUT'])
def update_synthetic_test(test_id):
    """Atualiza um teste sintético"""
    test = SyntheticTest.query.get_or_404(test_id)
    data = request.get_json()
    
    if data.get('test_name'):
        test.test_name = data['test_name']
    if data.get('site_url'):
        test.site_url = data['site_url']
    if data.get('email'):
        test.email = data['email']
    if data.get('password'):
        test.password = data['password']
    if data.get('product_name'):
        test.product_name = data['product_name']
    if data.get('address'):
        test.address = data['address']
    if data.get('payment_method'):
        test.payment_method = data['payment_method']
    if 'headless' in data:
        test.headless = data['headless']
    if 'is_active' in data:
        test.is_active = data['is_active']
    
    db.session.commit()
    return jsonify(test.to_dict())

@synthetic_bp.route('/synthetic-tests/<int:test_id>', methods=['DELETE'])
def delete_synthetic_test(test_id):
    """Remove um teste sintético"""
    test = SyntheticTest.query.get_or_404(test_id)
    db.session.delete(test)
    db.session.commit()
    return jsonify({'message': 'Teste removido com sucesso'})

@synthetic_bp.route('/synthetic-tests/<int:test_id>/execute', methods=['POST'])
def execute_synthetic_test(test_id):
    """Executa um teste sintético"""
    test = SyntheticTest.query.get_or_404(test_id)
    
    if not test.is_active:
        return jsonify({'error': 'Teste está inativo'}), 400
    
    # Inicia execução assíncrona
    execute_test_async(test_id, request.environ.get('flask.app'))
    
    return jsonify({
        'message': f'Teste {test.test_name} iniciado',
        'test_id': test_id
    })

@synthetic_bp.route('/synthetic-tests/<int:test_id>/results', methods=['GET'])
def get_synthetic_test_results(test_id):
    """Obtém resultados de um teste sintético"""
    test = SyntheticTest.query.get_or_404(test_id)
    
    # Parâmetros de filtro
    hours = request.args.get('hours', 24, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    since = get_brazil_datetime_for_db() - timedelta(hours=hours)
    
    results = SyntheticTestResult.query.filter(
        SyntheticTestResult.test_id == test_id,
        SyntheticTestResult.executed_at >= since
    ).order_by(SyntheticTestResult.executed_at.desc()).limit(limit).all()
    
    return jsonify([result.to_dict() for result in results])

@synthetic_bp.route('/synthetic-tests/<int:test_id>/results/<int:result_id>/steps', methods=['GET'])
def get_synthetic_test_steps(test_id, result_id):
    """Obtém passos detalhados de um resultado de teste"""
    test = SyntheticTest.query.get_or_404(test_id)
    result = SyntheticTestResult.query.get_or_404(result_id)
    
    if result.test_id != test_id:
        return jsonify({'error': 'Resultado não pertence ao teste'}), 400
    
    steps = SyntheticTestStep.query.filter_by(result_id=result_id).order_by(SyntheticTestStep.step_number).all()
    
    return jsonify([step.to_dict() for step in steps])

@synthetic_bp.route('/synthetic-stats', methods=['GET'])
def get_synthetic_stats():
    """Obtém estatísticas dos testes sintéticos"""
    # Parâmetros de filtro
    hours = request.args.get('hours', 24, type=int)
    
    since = get_brazil_datetime_for_db() - timedelta(hours=hours)
    
    # Total de testes ativos
    active_tests = SyntheticTest.query.filter_by(is_active=True).count()
    
    # Resultados no período
    results = SyntheticTestResult.query.filter(SyntheticTestResult.executed_at >= since).all()
    
    if not results:
        return jsonify({
            'active_tests': active_tests,
            'success_rate': 0,
            'total_executions': 0,
            'avg_duration': 0,
            'period_hours': hours
        })
    
    # Taxa de sucesso
    successful_results = [r for r in results if r.status == 'success']
    success_rate = (len(successful_results) / len(results)) * 100
    
    # Duração média
    durations = [r.duration for r in results if r.duration]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    return jsonify({
        'active_tests': active_tests,
        'success_rate': round(success_rate, 1),
        'total_executions': len(results),
        'avg_duration': round(avg_duration, 1),
        'period_hours': hours
    })

