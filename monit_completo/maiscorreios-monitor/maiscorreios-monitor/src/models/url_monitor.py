from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
from src.utils.timezone import get_brazil_datetime_for_db

db = SQLAlchemy()

class MonitoredURL(db.Model):
    __tablename__ = 'monitored_urls'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    url = db.Column(db.String(500), nullable=False, unique=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_brazil_datetime_for_db)
    
    # Relacionamento com verificações
    checks = db.relationship('URLCheck', backref='monitored_url', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<MonitoredURL {self.name}: {self.url}>'
    
    def to_dict(self):
        latest_check = URLCheck.query.filter_by(url_id=self.id).order_by(URLCheck.checked_at.desc()).first()
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'latest_check': latest_check.to_dict() if latest_check else None
        }

class URLCheck(db.Model):
    __tablename__ = 'url_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.Integer, db.ForeignKey('monitored_urls.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'online', 'offline', 'error'
    response_time = db.Column(db.Float)  # em segundos
    status_code = db.Column(db.Integer)
    error_message = db.Column(db.Text)
    checked_at = db.Column(db.DateTime, default=get_brazil_datetime_for_db)
    
    def __repr__(self):
        return f'<URLCheck {self.url_id}: {self.status} at {self.checked_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'url_id': self.url_id,
            'status': self.status,
            'response_time': self.response_time,
            'status_code': self.status_code,
            'error_message': self.error_message,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None
        }

