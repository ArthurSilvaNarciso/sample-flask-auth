from flask import Flask, request, jsonify
from models.user import User
from database import db
from flask_login import LoginManager, login_user, current_user

app = Flask(__name__)
app.config["SECRET_KEY"] = "your secret key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desabilitar o monitoramento de modificações no banco de dados

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
        data = request.get_json()  # Usar request.get_json() em vez de request.json
        if not data:
            return jsonify({"message": "Bad request: Missing JSON"}), 400

        username = data.get("username")
        password = data.get("password")

        if username and password:
            # LOGIN
            user = User.query.filter_by(username=username).first()
            if user and user.password == password:
                login_user(user)
                return jsonify({"message": "Autenticação realizada com sucesso"})
        
        return jsonify({"message": "Invalid username or password"}), 400

    except Exception as e:
        print(f"Erro: {e}")  # Exibir erro no console
        return jsonify({"message": "Erro interno no servidor. Tente novamente mais tarde."}), 500

@app.route('/Hello World', methods=['GET'])
def hello_world():
    return 'Hello World!'

if __name__ == "__main__":
    app.run(debug=True)
