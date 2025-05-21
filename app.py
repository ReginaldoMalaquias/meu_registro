# meu_registro/app.py

from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3
import os # Importar para verificar existência do arquivo do BD

app = Flask(__name__)
DATABASE = 'registro.db'

# Função para conectar ao banco de dados
def get_db():
    # Verifica se a conexão já existe no contexto global da requisição
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row # Para retornar linhas como dicionários
    return g.db

# Função para fechar a conexão do banco de dados ao final da requisição
@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Função para inicializar o banco de dados (criar tabelas se não existirem)
def init_db():
    with app.app_context(): # Garante que estamos no contexto da aplicação
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tarefas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                data_conclusao TEXT,
                status TEXT DEFAULT 'Pendente'
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cursos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                instituicao TEXT,
                progresso TEXT DEFAULT 'Não Iniciado'
            )
        ''')
        db.commit()
        # db.close() # Não fechar aqui, pois get_db gerencia a conexão

# Chamada para inicializar o banco de dados quando o aplicativo for executado
# Isso garante que as tabelas sejam criadas na primeira vez que o app for iniciado
if not os.path.exists(DATABASE):
    init_db()

# Rotas da Aplicação (restante do código permanece o mesmo)

@app.route('/')
def index():
    db = get_db()
    tarefas = db.execute('SELECT * FROM tarefas').fetchall()
    cursos = db.execute('SELECT * FROM cursos').fetchall()
    # Não precisa fechar db aqui, pois close_db fará isso no final da requisição
    return render_template('index.html', tarefas=tarefas, cursos=cursos)

@app.route('/adicionar_tarefa', methods=['POST'])
def adicionar_tarefa():
    nome = request.form['nome']
    data_conclusao = request.form['data_conclusao']
    db = get_db()
    db.execute('INSERT INTO tarefas (nome, data_conclusao) VALUES (?, ?)', (nome, data_conclusao))
    db.commit()
    return redirect(url_for('index'))

@app.route('/atualizar_status_tarefa/<int:id>', methods=['POST'])
def atualizar_status_tarefa(id):
    status = request.form['status']
    db = get_db()
    db.execute('UPDATE tarefas SET status = ? WHERE id = ?', (status, id))
    db.commit()
    return redirect(url_for('index'))

@app.route('/excluir_tarefa/<int:id>', methods=['POST'])
def excluir_tarefa(id):
    db = get_db()
    db.execute('DELETE FROM tarefas WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))

@app.route('/adicionar_curso', methods=['POST'])
def adicionar_curso():
    nome = request.form['nome']
    instituicao = request.form['instituicao']
    db = get_db()
    db.execute('INSERT INTO cursos (nome, instituicao) VALUES (?, ?)', (nome, instituicao))
    db.commit()
    return redirect(url_for('index'))

@app.route('/atualizar_progresso_curso/<int:id>', methods=['POST'])
def atualizar_progresso_curso(id):
    progresso = request.form['progresso']
    db = get_db()
    db.execute('UPDATE cursos SET progresso = ? WHERE id = ?', (progresso, id))
    db.commit()
    return redirect(url_for('index'))

@app.route('/excluir_curso/<int:id>', methods=['POST'])
def excluir_curso(id):
    db = get_db()
    db.execute('DELETE FROM cursos WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)