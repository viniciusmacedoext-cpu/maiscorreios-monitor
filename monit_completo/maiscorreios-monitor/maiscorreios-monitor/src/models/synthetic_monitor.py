from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from src.models.url_monitor import db
from src.utils.timezone import get_brazil_datetime_for_db

class SyntheticTest(db.Model):
    __tablename__ = 'synthetic_tests'
    
    id = db.Column(db.Integer, primary_key=True)
    test_name = db.Column(db.String(200), nullable=False)
    site_url = db.Column(db.String(500), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(500), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    headless = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=get_brazil_datetime_for_db)
    
    # Relacionamento com resultados
    results = db.relationship('SyntheticTestResult', backref='synthetic_test', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<SyntheticTest {self.test_name}: {self.site_url}>'
    
    def to_dict(self):
        latest_result = SyntheticTestResult.query.filter_by(test_id=self.id).order_by(SyntheticTestResult.executed_at.desc()).first()
        return {
            'id': self.id,
            'test_name': self.test_name,
            'site_url': self.site_url,
            'email': self.email,
            'password': self.password,
            'product_name': self.product_name,
            'address': self.address,
            'payment_method': self.payment_method,
            'is_active': self.is_active,
            'headless': self.headless,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'latest_result': latest_result.to_dict() if latest_result else None
        }

class SyntheticTestResult(db.Model):
    __tablename__ = 'synthetic_test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    test_id = db.Column(db.Integer, db.ForeignKey('synthetic_tests.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'success', 'failed', 'error'
    steps_completed = db.Column(db.Integer, default=0)
    total_steps = db.Column(db.Integer, default=8)
    duration = db.Column(db.Float)  # em segundos
    error_message = db.Column(db.Text)
    executed_at = db.Column(db.DateTime, default=get_brazil_datetime_for_db)
    
    def __repr__(self):
        return f'<SyntheticTestResult {self.test_id}: {self.status} at {self.executed_at}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'test_id': self.test_id,
            'status': self.status,
            'steps_completed': self.steps_completed,
            'total_steps': self.total_steps,
            'duration': self.duration,
            'error_message': self.error_message,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }

class SyntheticTestStep(db.Model):
    __tablename__ = 'synthetic_test_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    result_id = db.Column(db.Integer, db.ForeignKey('synthetic_test_results.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    step_name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # 'success', 'failed', 'error'
    duration = db.Column(db.Float)  # em segundos
    error_message = db.Column(db.Text)
    executed_at = db.Column(db.DateTime, default=get_brazil_datetime_for_db)
    
    def __repr__(self):
        return f'<SyntheticTestStep {self.result_id}: Step {self.step_number} - {self.status}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'result_id': self.result_id,
            'step_number': self.step_number,
            'step_name': self.step_name,
            'status': self.status,
            'duration': self.duration,
            'error_message': self.error_message,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None
        }

