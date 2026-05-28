import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, EnglishTask, WorkTask, FinancialContribution
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'g4s_premium_saas_encryption_key_2026'

DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://neondb_owner:npg_wgjp3WLGqI4b@ep-mute-star-apk4xjk6-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,  # Testa a conexão antes de usar. Se caiu, reconecta.
    "pool_recycle": 300     # Recicla a conexão a cada 5 minutos para evitar timeouts do servidor.
}

db.init_app(app)

with app.app_context():
    db.create_all()
    if not User.query.first():
        mock_user = User(name="Intercambista Pro", email="seu_email@linkeding4s.com")
        db.session.add(mock_user)
        db.session.commit()
        print("🚀 Base de dados e utilizador inicializados com sucesso.")

@app.route('/')
def index():
    user = User.query.first()
    english_tasks = EnglishTask.query.filter_by(user_id=user.id).order_by(EnglishTask.date.desc()).all()
    work_tasks = WorkTask.query.filter_by(user_id=user.id).order_by(WorkTask.due_date.asc()).all()
    contributions = FinancialContribution.query.filter_by(user_id=user.id).order_by(FinancialContribution.date.desc()).all()
    
    # Métricas Financeiras
    meta_final = 55000.00
    total_acumulado = sum([float(c.amount) for c in contributions])
    # Mudança para float com 2 casas decimais
    progresso_percentual = round((total_acumulado / meta_final) * 100, 2) if total_acumulado > 0 else 0.0
    if progresso_percentual > 100: progresso_percentual = 100.0

    # Métricas de Inglês
    eng_total = len(english_tasks)
    eng_done = len([t for t in english_tasks if t.completed])
    eng_percent = int((eng_done / eng_total) * 100) if eng_total > 0 else 0
    
    last_done_task = next((t for t in english_tasks if t.completed), None)
    last_report = last_done_task.learning_report if last_done_task else "Nenhum relatório consolidado."

    # Métricas de Trabalho
    urgentes = len([t for t in work_tasks if t.urgency == 'Urgente'])
    prioridades = len([t for t in work_tasks if t.urgency == 'Prioridade'])
    regulares = len([t for t in work_tasks if t.urgency == 'Regular'])
    total_work = len(work_tasks)

    return render_template('index.html', 
                           english_tasks=english_tasks, 
                           work_tasks=work_tasks, 
                           total_acumulado=total_acumulado,
                           progresso_percentual=progresso_percentual,
                           eng_total=eng_total,
                           eng_done=eng_done,
                           eng_percent=eng_percent,
                           last_report=last_report,
                           urgentes=urgentes,
                           prioridades=prioridades,
                           regulares=regulares,
                           total_work=total_work)

@app.route('/modulo-ingles')
def modulo_ingles():
    user = User.query.first()
    tasks = EnglishTask.query.filter_by(user_id=user.id).order_by(EnglishTask.date.desc()).all()
    return render_template('ingles.html', tasks=tasks)

@app.route('/modulo-trabalho')
def modulo_trabalho():
    user = User.query.first()
    tasks = WorkTask.query.filter_by(user_id=user.id).order_by(WorkTask.due_date.asc()).all()
    return render_template('trabalho.html', tasks=tasks)

@app.route('/modulo-financeiro')
def modulo_financeiro():
    user = User.query.first()
    contributions = FinancialContribution.query.filter_by(user_id=user.id).order_by(FinancialContribution.date.desc()).all()
    
    meta_final = 55000.00
    total_acumulado = sum([float(c.amount) for c in contributions])
    progresso_percentual = int((total_acumulado / meta_final) * 100) if total_acumulado > 0 else 0
    
    return render_template('financeiro.html', 
                           contributions=contributions, 
                           total_acumulado=total_acumulado, 
                           progresso_percentual=progresso_percentual)

# --- POST ACTIONS ---
@app.route('/english/add', methods=['POST'])
def add_english_task():
    user = User.query.first()
    new_task = EnglishTask(
        user_id=user.id,
        title=request.form.get('title'),
        date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
        time=datetime.strptime(request.form.get('time'), '%H:%M').time(),
        description=request.form.get('description')
    )
    db.session.add(new_task)
    db.session.commit()
    flash('Sessão de inglês agendada com sucesso.')
    return redirect(url_for('modulo_ingles'))

@app.route('/english/complete/<int:id>', methods=['POST'])
def complete_english_task(id):
    task = EnglishTask.query.get_or_404(id)
    report = request.form.get('learning_report')
    if not report or len(report.strip()) < 10:
        flash('Erro: O relatório de aprendizagem deve conter pelo menos 10 caracteres.')
        return redirect(url_for('modulo_ingles'))
    task.learning_report = report
    task.completed = True
    db.session.commit()
    flash('Sessão concluída e relatório arquivado.')
    return redirect(url_for('modulo_ingles'))

@app.route('/work/add', methods=['POST'])
def add_work_task():
    user = User.query.first()
    new_task = WorkTask(
        user_id=user.id,
        title=request.form.get('title'),
        start_date=datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date(),
        due_date=datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date(),
        urgency=request.form.get('urgency'),
        emails_together=request.form.get('emails_together')
    )
    db.session.add(new_task)
    db.session.commit()
    flash('Tarefa/Reunião mapeada e sincronizada.')
    return redirect(url_for('modulo_trabalho'))

@app.route('/finance/add', methods=['POST'])
def add_contribution():
    user = User.query.first()
    new_contribution = FinancialContribution(
        user_id=user.id,
        date=datetime.strptime(request.form.get('date'), '%Y-%m-%d').date(),
        amount=float(request.form.get('amount')),
        observation=request.form.get('observation')
    )
    db.session.add(new_contribution)
    db.session.commit()
    flash('Aporte financeiro consolidado.')
    return redirect(url_for('modulo_financeiro'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)