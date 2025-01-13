from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = "your secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar o banco de dados e o LoginManager
login_manager = LoginManager()
db.init_app(app)
login_manager.init_app(app)

# Criar as tabelas do banco de dados (caso não existam)
with app.app_context():
    db.create_all()

# View Login
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"message": "Bad request: Missing JSON"}), 400

        username = data.get("username")
        password = data.get("password")

        if username and password:
            # LOGIN
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return jsonify({"message": "Autenticação realizada com sucesso"})
        
        return jsonify({"message": "Invalid username or password"}), 400

    except Exception as e:
        print(f"Erro: {e}")
        return jsonify({"message": "Erro interno no servidor. Tente novamente mais tarde."}), 500

@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout realizado com sucesso"})

@app.route('/user', methods=['POST'])
def create_user():  
    data = request.get_json()  # Alterado para request.get_json()
    username = data.get("username") 
    password = data.get("password")

    if not username or not password:
        return jsonify({"message": "Username e password são obrigatórios."}), 400
    
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "Nome de usuário já existe."}), 400

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Usuário criado com sucesso"})

@app.route('/user/<int:id>', methods=['GET'])  # Corrigido a rota
def read_user(id):  # Corrigido para usar 'id'
    user = User.query.get(id)
    if user:
        return jsonify({"username": user.username})
    return jsonify({"message": "Usuário não encontrado"}), 404

@app.route('/user/<int:id>', methods=['PUT'])  # Corrigido a rota
@login_required
def update_user(id):  # Corrigido para usar 'id'
    data = request.get_json()
    user = User.query.get(id)
    if user and data.get('password'):
        user.password = data.get('password')       
        db.session.commit()
        
        return jsonify({"message": f"Usuario {id} atualizado com sucesso"}) 
    
    return jsonify({"message": "Usuário não encontrado"}), 404

@app.route('/user/<int:id>', methods=['DELETE'])  # Corrigido a rota
def delete_user(id):  # Corrigido para usar 'id'
    user = User.query.get(id)

    if id == current_user.id:
        return jsonify({"message": "Não é possível deletar o usuário logado"}), 403
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": f"Usuário {id} deletado com sucesso"})
    return jsonify({"message": "Usuário não encontrado"}), 404 



if __name__ == "__main__":
    app.run(debug=True)
 