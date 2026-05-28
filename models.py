from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    # Relacionamentos
    english_tasks = db.relationship('EnglishTask', backref='user', lazy=True)
    work_tasks = db.relationship('WorkTask', backref='user', lazy=True)
    financial_contributions = db.relationship('FinancialContribution', backref='user', lazy=True)

class EnglishTask(db.Model):
    __tablename__ = 'english_tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    learning_report = db.Column(db.Text, nullable=True) # Regra de Conclusão Obrigatória
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class WorkTask(db.Model):
    __tablename__ = 'work_tasks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    urgency = db.Column(db.String(20), nullable=False) # 'Urgente', 'Prioridade', 'Regular'
    emails_together = db.Column(db.Text, nullable=True) # Lista de e-mails separados por vírgula
    google_event_id = db.Column(db.String(255), nullable=True) # Sincronização API

class FinancialContribution(db.Model):
    __tablename__ = 'financial_contributions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    observation = db.Column(db.String(255), nullable=True)