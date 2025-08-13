from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Usar o mesmo db da url_monitor
from src.models.url_monitor import db

class SyntheticTest(db.Model):
    __tablename__ = 'synthetic_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(200), nullable=False)
    test_type = db.Column(db.String(50), nullable=False)  # 'purchase_flow', 'login_test', etc.
    site_url = db.Column(db.String(500), nullable=False)
    config_json = db.Column(db.Text)  # Configurações do teste em JSON
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now())
    
    # Relacionamento com resultados
    results = db.relationship('SyntheticResult', backref='synthetic_test', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SyntheticTest {self.test_name}>'
    
    def to_dict(self):
        latest_result = SyntheticResult.query.filter_by(test_id=self.id).order_by(SyntheticResult.executed_at.desc()).first()
        return {
            'id': self.id,
            'test_name': self.test_name,
            'test_type': self.test_type,
            'site_url': self.site_url,
            'config': json.loads(self.config_json) if self.config_json else {},
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'latest_status': latest_result.status if latest_result else None,
            'latest_execution': latest_result.executed_at.isoformat() if latest_result else None,
            'latest_duration': latest_result.duration_seconds if latest_result else None
        }

class SyntheticResult(db.Model):
    __tablename__ = 'synthetic_results'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('synthetic_tests.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'success', 'failed', 'partial'
    duration_seconds = db.Column(db.Float)
    steps_completed = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer, default=0)
    success_rate = db.Column(db.Float, default=0.0)  # Percentual de sucesso
    error_message = db.Column(db.Text)
    executed_at = db.Column(db.DateTime, default=lambda: datetime.now())
    
    # Relacionamento com passos
    steps = db.relationship('SyntheticStep', backref='synthetic_result', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SyntheticResult {self.test_id}: {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'test_id': self.test_id,
            'status': self.status,
            'duration_seconds': self.duration_seconds,
            'steps_completed': self.steps_completed,
            'total_steps': self.total_steps,
            'success_rate': self.success_rate,
            'error_message': self.error_message,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }

class SyntheticStep(db.Model):
    __tablename__ = 'synthetic_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('synthetic_results.id'), nullable=False)
    step_name = db.Column(db.String(100), nullable=False)
    step_order = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'success', 'failed', 'skipped'
    duration_seconds = db.Column(db.Float)
    error_message = db.Column(db.Text)
    screenshot_path = db.Column(db.String(500))
    executed_at = db.Column(db.DateTime, default=lambda: datetime.now())
    
    def __repr__(self):
        return f'<SyntheticStep {self.step_name}: {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'result_id': self.result_id,
            'step_name': self.step_name,
            'step_order': self.step_order,
            'status': self.status,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'screenshot_path': self.screenshot_path,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }

