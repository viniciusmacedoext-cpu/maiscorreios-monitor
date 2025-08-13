from flask import Blueprint, jsonify, request
from src.models.url_monitor import db, MonitoredURL, URLCheck
from datetime import datetime, timedelta
import requests
import time
import threading

monitor_bp = Blueprint('monitor', __name__)

def check_url_status(url):
    """Verifica o status de uma URL"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30, allow_redirects=True)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            return {
                'status': 'online',
                'response_time': response_time,
                'status_code': response.status_code,
                'error_message': None
            }
        else:
            return {
                'status': 'offline',
                'response_time': response_time,
                'status_code': response.status_code,
                'error_message': f'HTTP {response.status_code}'
            }
    except requests.exceptions.Timeout:
        return {
            'status': 'offline',
            'response_time': None,
            'status_code': None,
            'error_message': 'Timeout - Site não respondeu em 30 segundos'
        }
    except requests.exceptions.ConnectionError:
        return {
            'status': 'offline',
            'response_time': None,
            'status_code': None,
            'error_message': 'Erro de conexão - Site inacessível'
        }
    except Exception as e:
        return {
            'status': 'offline',
            'response_time': None,
            'status_code': None,
            'error_message': f'Erro: {str(e)}'
        }

@monitor_bp.route('/urls', methods=['GET'])
def get_urls():
    """Lista todas as URLs monitoradas"""
    try:
        urls = MonitoredURL.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'urls': [url.to_dict() for url in urls]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitor_bp.route('/urls', methods=['POST'])
def add_url():
    """Adiciona uma nova URL para monitoramento"""
    try:
        data = request.get_json()
        
        if not data or not data.get('url') or not data.get('name'):
            return jsonify({
                'success': False,
                'error': 'URL e nome são obrigatórios'
            }), 400
        
        # Verifica se a URL já existe
        existing = MonitoredURL.query.filter_by(url=data['url']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'Esta URL já está sendo monitorada'
            }), 400
        
        # Cria nova URL
        new_url = MonitoredURL(
            name=data['name'],
            url=data['url']
        )
        
        db.session.add(new_url)
        db.session.commit()
        
        # Faz uma verificação inicial
        check_result = check_url_status(data['url'])
        initial_check = URLCheck(
            url_id=new_url.id,
            status=check_result['status'],
            response_time=check_result['response_time'],
            status_code=check_result['status_code'],
            error_message=check_result['error_message']
        )
        
        db.session.add(initial_check)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'url': new_url.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitor_bp.route('/urls/<int:url_id>', methods=['DELETE'])
def delete_url(url_id):
    """Remove uma URL do monitoramento"""
    try:
        url = MonitoredURL.query.get_or_404(url_id)
        url.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'URL removida do monitoramento'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitor_bp.route('/urls/<int:url_id>/check', methods=['POST'])
def check_single_url(url_id):
    """Verifica uma URL específica"""
    try:
        url = MonitoredURL.query.get_or_404(url_id)
        
        check_result = check_url_status(url.url)
        new_check = URLCheck(
            url_id=url.id,
            status=check_result['status'],
            response_time=check_result['response_time'],
            status_code=check_result['status_code'],
            error_message=check_result['error_message']
        )
        
        db.session.add(new_check)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'check': new_check.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitor_bp.route('/check-all', methods=['POST'])
def check_all_urls():
    """Verifica todas as URLs ativas"""
    try:
        urls = MonitoredURL.query.filter_by(is_active=True).all()
        
        def check_url_async(url):
            check_result = check_url_status(url.url)
            new_check = URLCheck(
                url_id=url.id,
                status=check_result['status'],
                response_time=check_result['response_time'],
                status_code=check_result['status_code'],
                error_message=check_result['error_message']
            )
            db.session.add(new_check)
        
        # Verifica todas as URLs
        for url in urls:
            check_url_async(url)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(urls)} URLs verificadas'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitor_bp.route('/urls/<int:url_id>/history', methods=['GET'])
def get_url_history(url_id):
    """Obtém o histórico de verificações de uma URL"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        checks = URLCheck.query.filter_by(url_id=url_id)\
                              .order_by(URLCheck.checked_at.desc())\
                              .limit(limit).all()
        
        return jsonify({
            'success': True,
            'history': [check.to_dict() for check in checks]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitor_bp.route('/stats', methods=['GET'])
def get_stats():
    """Obtém estatísticas gerais do monitoramento"""
    try:
        total_urls = MonitoredURL.query.filter_by(is_active=True).count()
        
        # URLs online (última verificação)
        online_urls = 0
        offline_urls = 0
        
        for url in MonitoredURL.query.filter_by(is_active=True).all():
            latest_check = URLCheck.query.filter_by(url_id=url.id)\
                                        .order_by(URLCheck.checked_at.desc()).first()
            if latest_check:
                if latest_check.status == 'online':
                    online_urls += 1
                else:
                    offline_urls += 1
        
        # Verificações nas últimas 24h
        yesterday = datetime.now() - timedelta(hours=24)
        checks_24h = URLCheck.query.filter(URLCheck.checked_at >= yesterday).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_urls': total_urls,
                'online_urls': online_urls,
                'offline_urls': offline_urls,
                'checks_last_24h': checks_24h
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitor_bp.route('/consolidated-data', methods=['GET'])
def get_consolidated_data():
    """Obtém dados consolidados para gráfico"""
    try:
        hours = request.args.get('hours', 24, type=int)
        since = datetime.now() - timedelta(hours=hours)
        
        urls = MonitoredURL.query.filter_by(is_active=True).all()
        consolidated_data = []
        
        for url in urls:
            checks = URLCheck.query.filter_by(url_id=url.id)\
                                  .filter(URLCheck.checked_at >= since)\
                                  .order_by(URLCheck.checked_at.asc()).all()
            
            data_points = []
            for check in checks:
                data_points.append({
                    'timestamp': check.checked_at.isoformat(),
                    'response_time': check.response_time * 1000 if check.response_time else 0,
                    'status': check.status
                })
            
            consolidated_data.append({
                'url_name': url.name,
                'url_id': url.id,
                'data_points': data_points
            })
        
        return jsonify({
            'success': True,
            'consolidated_data': consolidated_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@monitor_bp.route('/performance-summary', methods=['GET'])
def get_performance_summary():
    """Obtém resumo de performance das URLs"""
    try:
        hours = request.args.get('hours', 24, type=int)
        since = datetime.now() - timedelta(hours=hours)
        
        urls = MonitoredURL.query.filter_by(is_active=True).all()
        summary = []
        
        for url in urls:
            checks = URLCheck.query.filter_by(url_id=url.id)\
                                  .filter(URLCheck.checked_at >= since).all()
            
            if not checks:
                continue
            
            response_times = [c.response_time for c in checks if c.response_time]
            online_checks = [c for c in checks if c.status == 'online']
            
            summary.append({
                'url_name': url.name,
                'url_id': url.id,
                'total_checks': len(checks),
                'online_checks': len(online_checks),
                'uptime_percentage': (len(online_checks) / len(checks)) * 100 if checks else 0,
                'avg_response_time': sum(response_times) / len(response_times) if response_times else 0,
                'min_response_time': min(response_times) if response_times else 0,
                'max_response_time': max(response_times) if response_times else 0
            })
        
        return jsonify({
            'success': True,
            'performance_summary': summary
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

