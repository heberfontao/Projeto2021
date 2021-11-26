from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, IntegerField, FloatField, DateField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from app.models import Usuario
from flask_login import current_user
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models import Acoes


class FormCriarConta(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    confirmacao_senha = PasswordField('Confirmação da Senha', validators=[DataRequired(), EqualTo('senha')])
    botao_submit_criarconta = SubmitField('Criar Conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('E-mail já cadastrado. Cadastre-se com outro e-mail ou faça login para continuar')


class FormLogin(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 20)])
    lembrar_dados = BooleanField('Lembrar Dados de Acesso')
    botao_submit_login = SubmitField('Fazer Login')


class FormEditarPerfil(FlaskForm):
    username = StringField('Nome de Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Atualizar Foto de Perfil', validators=[FileAllowed(['jpg', 'png'])])

    botao_submit_editarperfil = SubmitField('Confirmar Edição')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                raise ValidationError('Já existe um usuário com esse e-mail. Cadastre outro e-mail')


class FormCriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2, 140)])
    corpo = TextAreaField('Escreva seu Post Aqui', validators=[DataRequired()])
    botao_submit = SubmitField('Criar Post')


class FormAcoes(FlaskForm):
    ticker = StringField('Ticker da Ação', validators=[DataRequired(), Length(2, 140)])
    nome = StringField('Nome da Ação', validators=[DataRequired()])
    botao_submit_acao = SubmitField('Gravar Ação')

def choice_query():
    return Acoes.query

class FormCompras(FlaskForm):
    #id_acao = IntegerField('Id da Ação', validators=[DataRequired()])
    id_acao = QuerySelectField(query_factory=choice_query, allow_blank=True, get_label='ticker', validators=[DataRequired()])
    data = DateField('Data de Compra', validators=[DataRequired()])
    quantidade = IntegerField('Quantidade Adquirida', validators=[DataRequired()])
    valor_unitario = FloatField('Valor Unitário', validators=[DataRequired()])
    total_taxas = FloatField('Demais Taxas', validators=[DataRequired()])

    botao_submit_compras = SubmitField('Gravar Compra')

class FormVendas(FlaskForm):
    #id_acao = IntegerField('Id da Ação', validators=[DataRequired()])
    id_acao = QuerySelectField(query_factory=choice_query, allow_blank=True, get_label='ticker', validators=[DataRequired()])
    data = DateField('Data de Venda', validators=[DataRequired()])
    quantidade = IntegerField('Quantidade Vendida', validators=[DataRequired()])
    valor_unitario = FloatField('Valor Unitário', validators=[DataRequired()])
    total_taxas = FloatField('Demais Taxas', validators=[DataRequired()])

    botao_submit_vendas = SubmitField('Gravar Venda')

class FormApuracao(FlaskForm):
    data = StringField('Mês da Apuração', validators=[DataRequired()])
    botao_submit_apuracao = SubmitField('Gravar Apuração')


