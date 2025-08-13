from flask import Blueprint, jsonify, request
from src.models.synthetic_monitor import db, SyntheticTest, SyntheticResult, SyntheticStep
from src.synthetic_engine import MaisCorreiosSyntheticEngine
from datetime import datetime, timedelta
import json
import threading
import time
import traceback
## Alertas removidos a pedido do usuário

synthetic_bp = Blueprint('synthetic', __name__)

def execute_test_async(test_id, app=None):
    """Executa teste sintético de forma assíncrona"""
    from flask import current_app
    
    try:
        # Verifica se temos um contexto de aplicação
        if app:
            ctx = app.app_context()
            ctx.push()
        
        # Busca o teste
        test = SyntheticTest.query.get(test_id)
        if not test:
            return
        
        # Carrega configuração
        config = json.loads(test.config_json) if test.config_json else {}
        
        # Verifica se a configuração tem todos os campos necessários
        if not config.get('site_url'):
            config['site_url'] = test.site_url
        
        # Adiciona valores padrão para campos obrigatórios se não existirem
        if not config.get('email'):
            config['email'] = 'teste@exemplo.com'
        if not config.get('password'):
            config['password'] = 'senha123'
        if not config.get('product_name'):
            config['product_name'] = 'envelope'
        if not config.get('address'):
            config['address'] = 'Rua Exemplo, 123'
        
        # Executa o teste
        engine = MaisCorreiosSyntheticEngine(headless=config.get('headless', True))
        start_time = time.time()
        
        result = engine.execute_full_test(config)
        
        duration = time.time() - start_time
        
        # Salva resultado no banco
        synthetic_result = SyntheticResult(
            test_id=test.id,
            status=result['status'],
            duration_seconds=duration,
            steps_completed=result.get('steps_completed', 0),
            total_steps=result.get('total_steps', 0),
            success_rate=result.get('success_rate', 0.0),
            error_message=result.get('error')
        )
        
        db.session.add(synthetic_result)
        db.session.flush()  # Para obter o ID
        
        # Salva os passos
        for step_data in result.get('steps_results', []):
            step = SyntheticStep(
                result_id=synthetic_result.id,
                step_name=step_data['step_name'],
                step_order=step_data['step_order'],
                status=step_data['status'],
                duration_seconds=step_data['duration'],
                error_message=step_data.get('message'),
                screenshot_path=step_data.get('screenshot')
            )
            db.session.add(step)
        
        db.session.commit()
            
        # (alertas removidos)

        print(f"✅ Teste sintético {test.test_name} executado com sucesso")
        
    except Exception as e:
        print(f"❌ Erro na execução do teste sintético: {e}")
        print(traceback.format_exc())
        
        # Salva resultado de erro
        try:
            synthetic_result = SyntheticResult(
                test_id=test_id,
                status='failed',
                duration_seconds=time.time() - start_time if 'start_time' in locals() else 0,
                steps_completed=0,
                total_steps=6,
                success_rate=0.0,
                error_message=str(e)
            )
            db.session.add(synthetic_result)
            db.session.commit()
        except:
            pass
    finally:
        # Libera o contexto da aplicação se foi criado
        if app and 'ctx' in locals():
            ctx.pop()

@synthetic_bp.route('/synthetic-tests', methods=['GET'])
def get_synthetic_tests():
    """Lista todos os testes sintéticos"""
    try:
        tests = SyntheticTest.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'tests': [test.to_dict() for test in tests]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@synthetic_bp.route('/synthetic-tests', methods=['POST'])
def create_synthetic_test():
    """Cria um novo teste sintético"""
    try:
        data = request.get_json()
        
        if not data or not data.get('test_name') or not data.get('site_url'):
            return jsonify({
                'success': False,
                'error': 'Nome do teste e URL do site são obrigatórios'
            }), 400
        
        # Cria novo teste
        new_test = SyntheticTest(
            test_name=data['test_name'],
            test_type=data.get('test_type', 'purchase_flow'),
            site_url=data['site_url'],
            config_json=json.dumps(data.get('config', {}))
        )
        
        db.session.add(new_test)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'test': new_test.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@synthetic_bp.route('/synthetic-tests/<int:test_id>/execute', methods=['POST'])
def execute_synthetic_test(test_id):
    """Executa um teste sintético"""
    try:
        from flask import current_app
        test = SyntheticTest.query.get_or_404(test_id)
        
        # Executa o teste em thread separada para não bloquear a resposta
        # Passa o contexto da aplicação para a thread
        thread = threading.Thread(target=execute_test_async, args=(test_id, current_app._get_current_object()))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'message': 'Teste sintético iniciado com sucesso'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@synthetic_bp.route('/synthetic-tests/<int:test_id>/results', methods=['GET'])
def get_test_results(test_id):
    """Obtém resultados de um teste sintético"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        results = SyntheticResult.query.filter_by(test_id=test_id)\
                                     .order_by(SyntheticResult.executed_at.desc())\
                                     .limit(limit).all()
        
        return jsonify({
            'success': True,
            'results': [result.to_dict() for result in results]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@synthetic_bp.route('/synthetic-results/<int:result_id>/steps', methods=['GET'])
def get_result_steps(result_id):
    """Obtém passos de um resultado específico"""
    try:
        steps = SyntheticStep.query.filter_by(result_id=result_id)\
                                  .order_by(SyntheticStep.step_order.asc()).all()
        
        return jsonify({
            'success': True,
            'steps': [step.to_dict() for step in steps]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@synthetic_bp.route('/synthetic-stats', methods=['GET'])
def get_synthetic_stats():
    """Obtém estatísticas dos testes sintéticos"""
    try:
        total_tests = SyntheticTest.query.filter_by(is_active=True).count()
        
        # Resultados das últimas 24h
        yesterday = datetime.now() - timedelta(hours=24)
        recent_results = SyntheticResult.query.filter(SyntheticResult.executed_at >= yesterday).all()
        
        total_executions = len(recent_results)
        successful_executions = len([r for r in recent_results if r.status == 'success'])
        
        # Se não houver execuções, evita divisão por zero
        success_rate = (successful_executions / total_executions * 100) if total_executions > 0 else 0
        
        # Tempo médio de execução
        avg_duration = sum([r.duration_seconds for r in recent_results if r.duration_seconds]) / total_executions if total_executions > 0 else 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total_tests': total_tests,
                'executions_24h': total_executions,
                'success_rate': success_rate,
                'avg_duration': avg_duration
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Rota para criar um teste padrão se não existir nenhum
@synthetic_bp.route('/synthetic-tests/create-default', methods=['POST'])
def create_default_test():
    """Cria um teste sintético padrão se não existir nenhum"""
    try:
        # Verifica se já existe algum teste
        existing_tests = SyntheticTest.query.count()
        
        if existing_tests > 0:
            return jsonify({
                'success': False,
                'message': 'Já existem testes sintéticos cadastrados'
            })
        
        # Cria teste padrão
        default_test = SyntheticTest(
            test_name='Fluxo de Compra - Mais Correios',
            test_type='purchase_flow',
            site_url='https://www.maiscorreios.com.br',
            config_json=json.dumps({
                'email': 'teste@exemplo.com',
                'password': 'senha123',
                'product_name': 'envelope',
                'address': 'Rua Exemplo, 123'
            })
        )
        
        db.session.add(default_test)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'test': default_test.to_dict(),
            'message': 'Teste padrão criado com sucesso'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

