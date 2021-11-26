from app import database, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_usuario(id_usuario):
    return Usuario.query.get(int(id_usuario))


class Usuario(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String, nullable=False)
    email = database.Column(database.String, nullable=False, unique=True)
    senha = database.Column(database.String, nullable=False)
    foto_perfil = database.Column(database.String, default='default.jpg')
    posts = database.relationship('Post', backref='autor', lazy=True)
    cursos = database.Column(database.String, nullable=False, default='Não Informado')
    compras = database.relationship('Compras', backref='autor', lazy=True)
    vendas = database.relationship('Vendas', backref='autor', lazy=True)
    apuracao = database.relationship('Apuracao', backref='autor', lazy=True)

    def contar_posts(self):
        return len(self.posts)


class Post(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    titulo = database.Column(database.String, nullable=False)
    corpo = database.Column(database.Text, nullable=False)
    data_criacao = database.Column(database.DateTime, nullable=False, default=datetime.utcnow)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)



class Acoes(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    nome = database.Column(database.String, nullable=False)
    ticker = database.Column(database.String, nullable=False, unique=True)

    compras = database.relationship(
        "Compras", foreign_keys="[Compras.id_acao]", back_populates="acao"
    )
    vendas = database.relationship(
        "Vendas", foreign_keys="[Vendas.id_acao]", back_populates="acao"
    )

    def __init__(self, nome, ticker):
        self.nome = nome
        self.ticker = ticker

class Compras(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    id_acao = database.Column(database.Integer, database.ForeignKey("acoes.id"), nullable=False)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    data = database.Column(database.Integer, nullable=False)
    quantidade = database.Column(database.Integer, nullable=False)
    valor_unitario = database.Column(database.Numeric, nullable=False)
    total_taxas = database.Column(database.Numeric, nullable=False)
    custo = database.Column(database.Numeric, nullable=False)

    acao = database.relationship(
        "Acoes", foreign_keys=[id_acao], back_populates="compras"
    )

class Vendas(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    id_acao = database.Column(database.Integer, database.ForeignKey('acoes.id'), nullable=False)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    data = database.Column(database.Integer, nullable=False)
    quantidade = database.Column(database.Integer, nullable=False)
    valor_unitario = database.Column(database.Numeric, nullable=False)
    total_taxas = database.Column(database.Numeric, nullable=False)
    total_venda = database.Column(database.Numeric, nullable=False)
    resultado = database.Column(database.Numeric)

    acao = database.relationship(
        "Acoes", foreign_keys=[id_acao], back_populates="vendas"
    )

class Apuracao(database.Model):
    id = database.Column(database.Integer, primary_key=True, autoincrement=True)
    id_usuario = database.Column(database.Integer, database.ForeignKey('usuario.id'), nullable=False)
    data = database.Column(database.String, nullable=False)



