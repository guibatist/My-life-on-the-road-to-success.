import os
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User, EnglishTask, WorkTask, FinancialContribution
from datetime import datetime

app = Flask(__name__)
# Chave secreta necessária para usar o flash() e sessões no Flask
app.secret_key = 'g4s_strat_key_2026'

# --- CONFIGURAÇÃO DO NEONDB (POSTGRESQL) ---
# Substitua a string abaixo pela sua URL de conexão do NeonDB
DATABASE_URL = os.environ.get('DATABASE_URL','postgresql://neondb_owner:npg_wgjp3WLGqI4b@ep-mute-star-apk4xjk6-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require')
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# --- INICIALIZAÇÃO AUTOMÁTICA DO BANCO ---
with app.app_context():
    db.create_all()  # Cria as tabelas no banco de dados se elas não existirem
    
    # Cria um usuário padrão para o MVP se o banco estiver vazio
    if not User.query.first():
        mock_user = User(name="Intercambista Pro", email="seu_email@linkeding4s.com")
        db.session.add(mock_user)
        db.session.commit()
        print("🚀 Banco de dados inicializado e usuário base criado com sucesso!")

# --- ROTA PRINCIPAL (DASHBOARD) ---
@app.route('/')
def index():
    user = User.query.first()
    
    # Consultas do Banco de Dados
    english_tasks = EnglishTask.query.filter_by(user_id=user.id).order_by(EnglishTask.date.desc()).all()
    work_tasks = WorkTask.query.filter_by(user_id=user.id).order_by(WorkTask.due_date.asc()).all()
    contributions = FinancialContribution.query.filter_by(user_id=user.id).order_by(FinancialContribution.date.desc()).all()
    
    # Paleta de Urgência G4S
    urgency_colors = {'Urgente': '#D22630', 'Prioridade': '#FFBF00', 'Regular': '#002D62'}

    # Cálculos Financeiros
    meta_final = 55000.00
    total_acumulado = sum([float(c.amount) for c in contributions])
    progresso_percentual = round((total_acumulado / meta_final) * 100, 2) if total_acumulado > 0 else 0.0

    return render_template('index.html', 
                           english_tasks=english_tasks, 
                           work_tasks=work_tasks, 
                           contributions=contributions,
                           total_acumulado=total_acumulado,
                           meta_final=meta_final,
                           progresso_percentual=progresso_percentual,
                           urgency_colors=urgency_colors)

# --- ROTAS DO MÓDULO DE INGLÊS ---
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
    flash('Missão de inglês agendada!')
    return redirect(url_for('index'))

@app.route('/english/complete/<int:id>', methods=['POST'])
def complete_english_task(id):
    task = EnglishTask.query.get_or_404(id)
    report = request.form.get('learning_report')
    
    if not report or len(report.strip()) < 10:
        flash('Erro: Você precisa detalhar o relatório de aprendizado (mínimo 10 caracteres) para fechar este bloco!', 'error')
        return redirect(url_for('index'))
    
    task.learning_report = report
    task.completed = True
    db.session.commit()
    flash('Estudo consolidado e salvo no histórico!')
    return redirect(url_for('index'))

# --- ROTAS DO MÓDULO DE TRABALHO E NETWORKING ---
@app.route('/work/add', methods=['POST'])
def add_work_task():
    user = User.query.first()
    
    title = request.form.get('title')
    start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
    due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
    urgency = request.form.get('urgency')
    emails = request.form.get('emails_together')

    new_task = WorkTask(
        user_id=user.id,
        title=title,
        start_date=start_date,
        due_date=due_date,
        urgency=urgency,
        emails_together=emails
    )
    
    # TO-DO: Integração com o Google Calendar
    # Quando o script do Google estiver pronto, a chamada entrará aqui:
    # try:
    #     event_id = create_google_event(title, start_date, due_date, emails)
    #     new_task.google_event_id = event_id
    # except Exception as e:
    #     print(f"Erro no Calendar: {e}")
    
    db.session.add(new_task)
    db.session.commit()
    flash('Job/Reunião mapeada com sucesso!')
    return redirect(url_for('index'))

# --- ROTAS DO MÓDULO FINANCEIRO ---
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
    flash('Aporte na Caixinha registrado! Menos um dia para Cape Town.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Configuração ideal para rodar em ambientes como GitHub Codespaces ou local
    app.run(host='0.0.0.0', port=5000, debug=True)