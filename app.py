from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from collections import defaultdict
from datetime import datetime
from collections import Counter
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///denuncias.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo de denúncia
class Denuncia(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    categoria = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)


# Cria o banco se não existir, dentro do contexto da aplicação
if not os.path.exists('denuncias.db'):
    with app.app_context():
        db.create_all()

# -----------------------------
# Rotas do Frontend
# -----------------------------

# Tela inicial
@app.route('/')
def index():
    return render_template('index.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# -----------------------------
# Rotas de backend / API
# -----------------------------

# Receber denúncia via POST
@app.route('/enviar', methods=['POST'])
def enviar_denuncia():
    data = request.get_json()
    categoria = data.get('categoria')
    descricao = data.get('descricao')
    if not categoria or not descricao:
        return jsonify({'erro': 'Campos obrigatórios'}), 400

    denuncia = Denuncia(categoria=categoria, descricao=descricao)
    db.session.add(denuncia)
    db.session.commit()
    return jsonify({'sucesso': True}), 200

# API de estatísticas para dashboard
@app.route('/api/stats')
def api_stats():
    denuncias = Denuncia.query.all()

    # Contagem por categoria
    categorias = [d.categoria for d in denuncias]
    contagem_categoria = Counter(categorias)

    # Contagem por mês (YYYY-MM)
    meses = [d.data_criacao.strftime("%Y-%m") for d in denuncias]
    contagem_meses = Counter(meses)

    return jsonify({
        'total_categorias': dict(contagem_categoria),
        'total_meses': dict(contagem_meses),
        'total_geral': len(denuncias)
    })

@app.route('/api/denuncias')
def api_denuncias():
    denuncias = Denuncia.query.order_by(Denuncia.data_criacao.desc()).all()
    categorias = defaultdict(list)
    for d in denuncias:
        categorias[d.categoria].append({
            'descricao': d.descricao,
            'data_criacao': d.data_criacao.strftime("%Y-%m-%d %H:%M")
        })
    return jsonify(categorias)
# -----------------------------
# Rodar aplicação
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)
