import requests
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify
from src.models.url_monitor import db, MonitoredURL, URLCheck
from src.utils.timezone import get_brazil_datetime_for_db

monitor_bp = Blueprint('monitor', __name__)

def check_url_status(url, timeout=10):
    """Verifica o status de uma URL"""
    try:
        start_time = datetime.now()
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        end_time = datetime.now()
        
        response_time = (end_time - start_time).total_seconds()
        
        if response.status_code < 400:
            return 'online', response_time, response.status_code, None
        else:
            return 'offline', response_time, response.status_code, f"HTTP {response.status_code}"
            
    except requests.exceptions.Timeout:
        return 'offline', timeout, None, "Timeout"
    except requests.exceptions.ConnectionError:
        return 'offline', 0, None, "Connection Error"
    except Exception as e:
        return 'error', 0, None, str(e)

@monitor_bp.route('/urls', methods=['GET'])
def get_urls():
    """Lista todas as URLs monitoradas"""
    urls = MonitoredURL.query.all()
    return jsonify([url.to_dict() for url in urls])

@monitor_bp.route('/urls', methods=['POST'])
def add_url():
    """Adiciona uma nova URL para monitoramento"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('url'):
        return jsonify({'error': 'Nome e URL são obrigatórios'}), 400
    
    # Verifica se a URL já existe
    existing_url = MonitoredURL.query.filter_by(url=data['url']).first()
    if existing_url:
        return jsonify({'error': 'URL já está sendo monitorada'}), 400
    
    # Cria nova URL
    new_url = MonitoredURL(
        name=data['name'],
        url=data['url']
    )
    
    db.session.add(new_url)
    db.session.commit()
    
    # Faz primeira verificação
    status, response_time, status_code, error_message = check_url_status(data['url'])
    
    first_check = URLCheck(
        url_id=new_url.id,
        status=status,
        response_time=response_time,
        status_code=status_code,
        error_message=error_message
    )
    
    db.session.add(first_check)
    db.session.commit()
    
    return jsonify(new_url.to_dict()), 201

@monitor_bp.route('/urls/<int:url_id>', methods=['PUT'])
def update_url(url_id):
    """Atualiza uma URL monitorada"""
    url = MonitoredURL.query.get_or_404(url_id)
    data = request.get_json()
    
    if data.get('name'):
        url.name = data['name']
    if data.get('url'):
        url.url = data['url']
    if 'is_active' in data:
        url.is_active = data['is_active']
    
    db.session.commit()
    return jsonify(url.to_dict())

@monitor_bp.route('/urls/<int:url_id>', methods=['DELETE'])
def delete_url(url_id):
    """Remove uma URL do monitoramento"""
    url = MonitoredURL.query.get_or_404(url_id)
    db.session.delete(url)
    db.session.commit()
    return jsonify({'message': 'URL removida com sucesso'})

@monitor_bp.route('/urls/<int:url_id>/check', methods=['POST'])
def check_url(url_id):
    """Verifica uma URL específica"""
    url = MonitoredURL.query.get_or_404(url_id)
    
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
    
    return jsonify({
        'url_id': url.id,
        'status': status,
        'response_time': response_time,
        'status_code': status_code,
        'error_message': error_message,
        'checked_at': check.checked_at.isoformat() if check.checked_at else None
    })

@monitor_bp.route('/urls/<int:url_id>/history', methods=['GET'])
def get_url_history(url_id):
    """Obtém histórico de verificações de uma URL"""
    url = MonitoredURL.query.get_or_404(url_id)
    
    # Parâmetros de filtro
    hours = request.args.get('hours', 24, type=int)
    limit = request.args.get('limit', 100, type=int)
    
    since = get_brazil_datetime_for_db() - timedelta(hours=hours)
    
    checks = URLCheck.query.filter(
        URLCheck.url_id == url_id,
        URLCheck.checked_at >= since
    ).order_by(URLCheck.checked_at.desc()).limit(limit).all()
    
    return jsonify([check.to_dict() for check in checks])

@monitor_bp.route('/stats', methods=['GET'])
def get_stats():
    """Obtém estatísticas gerais do monitoramento"""
    # Parâmetros de filtro
    hours = request.args.get('hours', 24, type=int)
    
    since = get_brazil_datetime_for_db() - timedelta(hours=hours)
    
    # Total de URLs
    total_urls = MonitoredURL.query.filter_by(is_active=True).count()
    
    # URLs online/offline (baseado na última verificação)
    online_count = 0
    offline_count = 0
    
    urls = MonitoredURL.query.filter_by(is_active=True).all()
    for url in urls:
        latest_check = URLCheck.query.filter_by(url_id=url.id).order_by(URLCheck.checked_at.desc()).first()
        if latest_check:
            if latest_check.status == 'online':
                online_count += 1
            else:
                offline_count += 1
    
    # Total de verificações no período
    total_checks = URLCheck.query.filter(URLCheck.checked_at >= since).count()
    
    # Tempo médio de resposta
    avg_response_time = db.session.query(db.func.avg(URLCheck.response_time)).filter(
        URLCheck.checked_at >= since,
        URLCheck.status == 'online'
    ).scalar() or 0
    
    return jsonify({
        'total_urls': total_urls,
        'online_count': online_count,
        'offline_count': offline_count,
        'total_checks_24h': total_checks,
        'avg_response_time': round(avg_response_time, 2) if avg_response_time else 0,
        'period_hours': hours
    })

@monitor_bp.route('/overview', methods=['GET'])
def get_overview():
    """Obtém visão geral do monitoramento"""
    # Parâmetros de filtro
    hours = request.args.get('hours', 24, type=int)
    
    since = get_brazil_datetime_for_db() - timedelta(hours=hours)
    
    # URLs com suas últimas verificações
    urls = MonitoredURL.query.filter_by(is_active=True).all()
    url_data = []
    
    for url in urls:
        latest_check = URLCheck.query.filter_by(url_id=url.id).order_by(URLCheck.checked_at.desc()).first()
        
        # Verificações no período
        checks_in_period = URLCheck.query.filter(
            URLCheck.url_id == url.id,
            URLCheck.checked_at >= since
        ).count()
        
        url_data.append({
            'id': url.id,
            'name': url.name,
            'url': url.url,
            'is_active': url.is_active,
            'latest_check': latest_check.to_dict() if latest_check else None,
            'checks_in_period': checks_in_period
        })
    
    return jsonify(url_data)

