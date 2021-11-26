from flask import render_template, redirect, url_for, flash, request, abort
from app import app, database, bcrypt
from app.forms import FormLogin, FormCriarConta, FormEditarPerfil, FormCriarPost, FormAcoes, FormCompras, FormVendas, FormApuracao
from app.models import Usuario, Post, Acoes, Compras, Vendas, Apuracao
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image
import calendar
import datetime
import locale
from datetime import date, datetime
from app import database



@app.route('/')
def home():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('home.html', posts=posts)

@app.route('/acoes', methods=['GET', 'POST'])
@login_required
def acoes():
    form_acoes = FormAcoes()
    if form_acoes.validate_on_submit():
        acoes = Acoes(ticker=form_acoes.ticker.data, nome=form_acoes.nome.data)
        database.session.add(acoes)
        database.session.commit()
        flash('Ação Cadastrada com Sucesso', 'alert-success')
        return redirect(url_for('acoes_lista'))
    return render_template('acoes.html', form_acoes=form_acoes)

@app.route('/acoes/lista')
def acoes_lista():
    acoes = Acoes.query.order_by(Acoes.id.asc())
    return render_template('acoeslista.html', acoes=acoes)


@app.route('/contato')
def contato():
    return render_template('contato.html')

@app.route('/compras', methods=['GET', 'POST'])
@login_required
def compras():
    form_compras = FormCompras()
    if form_compras.validate_on_submit():

        #date = datetime.datetime.utcnow()
        #utc_time = calendar.timegm(date.utctimetuple())

        compras = Compras(id_acao=(form_compras.id_acao.data).id, autor=current_user, data=form_compras.data.data, quantidade=form_compras.quantidade.data, valor_unitario=form_compras.valor_unitario.data, total_taxas=form_compras.total_taxas.data, custo=(form_compras.valor_unitario.data * form_compras.quantidade.data)+form_compras.total_taxas.data)
        database.session.add(compras)
        database.session.commit()
        flash('Compra Registrada com Sucesso', 'alert-success')
        return redirect(url_for('compras_lista'))
    return render_template('compras.html', form_compras=form_compras)

@app.route('/compras/lista')
def compras_lista():
    compras = Compras.query.filter(Compras.id_usuario==current_user.id).order_by(Compras.id.asc())

    for compra in compras:
        #compra.data = datetime.datetime.fromtimestamp(compra.data).strftime('%d/%m/%Y')
        compra.data = date.fromisoformat(compra.data)
        compra.data_formatada = compra.data.strftime('%d/%m/%Y')

        if (compra.valor_unitario is not None):
            compra.valor = "R${:,.2f}".format(compra.valor_unitario)
        else:
            compra.valor = ''

        if (compra.total_taxas is not None):
            compra.taxas = "R${:,.2f}".format(compra.total_taxas)
        else:
            compra.taxas = ''

        if (compra.custo is not None):
            compra.custo_formatado = "R${:,.2f}".format(compra.custo)
        else:
            compra.custo_formatado = ''

    return render_template('compraslista.html', compras=compras)

@app.route('/vendas', methods=['GET', 'POST'])
@login_required
def vendas():
    form_vendas = FormVendas()
    if form_vendas.validate_on_submit():
        vendas = Vendas(id_acao=(form_vendas.id_acao.data).id, autor=current_user, data=form_vendas.data.data, quantidade=form_vendas.quantidade.data, valor_unitario=form_vendas.valor_unitario.data, total_taxas=form_vendas.total_taxas.data, total_venda=(form_vendas.valor_unitario.data * form_vendas.quantidade.data)-form_vendas.total_taxas.data, resultado='0.0')
        database.session.add(vendas)
        database.session.commit()
        flash('Compra Registrada com Sucesso', 'alert-success')
        return redirect(url_for('vendas_lista'))
    return render_template('vendas.html', form_vendas=form_vendas)

@app.route('/vendas/lista')
def vendas_lista():
    vendas = Vendas.query.filter(Vendas.id_usuario==current_user.id).order_by(Vendas.id.asc())

    for venda in vendas:

        #venda.data = datetime.datetime.fromtimestamp(venda.data).strftime('%d/%m/%Y')
        venda.data = date.fromisoformat(venda.data)
        venda.data_formatada = venda.data.strftime('%d/%m/%Y')


        if (venda.valor_unitario is not None):
            venda.valor = "R${:,.2f}".format(venda.valor_unitario)
        else:
            venda.valor = ''

        if (venda.total_taxas is not None):
            venda.taxas = "R${:,.2f}".format(venda.total_taxas)
        else:
            venda.taxas = ''

        if (venda.total_venda is not None):
            venda.total_formatado = "R${:,.2f}".format(venda.total_venda)
        else:
            venda.total_formatado = ''


    return render_template('vendaslista.html', vendas=vendas)


@app.route('/apuracao', methods=['GET', 'POST'])
@login_required
def apuracao():
    form_apuracao = FormApuracao()
    if form_apuracao.validate_on_submit():
        dataSplit = form_apuracao.data.data.split('/')
        dataFiltro = dataSplit[1] + '-' + dataSplit[0] 
        list = []
        totalResultado = 0
        totalGeralVendas = 0
        imposto = 0

        lista =  database.session.execute(
            """
                select ticker, 
                    sum(qtde_compra), 
                    sum(qtde_venda),
                    sum(custo), 
                    sum(total_venda),
                    ((sum(total_venda) / sum(qtde_venda)) - (sum(custo) / sum(qtde_compra))) * (sum(qtde_venda))
                    
                from (
                    select a.ticker,
                            c.quantidade qtde_compra,
                            0 qtde_venda,
                            c.custo,
                            0 total_venda
                    from compras c,
                            acoes a
                    where c.id_acao = a.id
	                and SUBSTR(c.data, 1, 7) = :data
	                and c.id_usuario = :user

                    UNION

                    select a.ticker,
                            0 qtde_compra,
                            v.quantidade qtde_venda,
                            0 custo,
                            v.total_venda
                    from acoes a,
                                    vendas v
                    where v.id_acao = a.id
	                and SUBSTR(v.data, 1, 7) = :data
	                and v.id_usuario = :user
                ) group by ticker
            """,
            {'data': dataFiltro, 'user': current_user.id},
        ).fetchall()

        for tupla in lista:
            item = {
                'ticker': tupla[0],
                'qtdeCompras': tupla[1],
                'qtdeVendas': tupla[2],
                'custo': "R${:,.2f}".format(tupla[3]),
                'totalVendas': "R${:,.2f}".format(tupla[4])


            }


            if tupla[5] is not None:
                totalResultado = totalResultado + tupla[5]
                item.update({'resultado': "R${:,.2f}".format(tupla[5])})

            if tupla[4] is not None:
                totalGeralVendas = totalGeralVendas + tupla[4]
                item.update({'totalGeralVendas': "R${:,.2f}".format(tupla[4])})

            list.append(item)

            if totalGeralVendas > 20000:
                if totalResultado > 0:
                    imposto = (totalResultado) * 15 / 100
            else:
                imposto = 0



        return render_template('apuracaolista.html', list=list, totalResultado=totalResultado, datacompetencia=form_apuracao.data.data, totalGeralVendas=totalGeralVendas, imposto=imposto)
    return render_template('apuracao.html', form_apuracao=form_apuracao)

# @app.route('/apuracao/lista')
# def apuracao_lista():
#     apuracao = Apuracao.query.order_by(Apuracao.id.asc())
#     return render_template('apuracaolista.html', apuracao=apuracao)


#@app.route('/estoque')
#def estoque():
    #estoque = Compras.query.order_by(Compras.data.asc())

     #return render_template('apuracaolista.html', apuracao=apuracao)

@app.route('/usuarios')
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template('usuarios.html', lista_usuarios=lista_usuarios)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form_login = FormLogin()
    form_criarconta = FormCriarConta()
    if form_login.validate_on_submit() and 'botao_submit_login' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Login feito com sucesso no e-mail: {form_login.email.data}', 'alert-success')
            par_next = request.args.get('next')
            if par_next:
                return redirect(par_next)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Falha no Login. E-mail ou Senha Incorretos', 'alert-danger')
    if form_criarconta.validate_on_submit() and 'botao_submit_criarconta' in request.form:
        senha_cript = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data, email=form_criarconta.email.data, senha=senha_cript)
        database.session.add(usuario)
        database.session.commit()
        flash(f'Conta criada para o e-mail: {form_criarconta.email.data}', 'alert-success')
        return redirect(url_for('home'))
    return render_template('login.html', form_login=form_login, form_criarconta=form_criarconta)


@app.route('/sair')
@login_required
def sair():
    logout_user()
    flash(f'Logout Feito com Sucesso', 'alert-success')
    return redirect(url_for('home'))


@app.route('/perfil')
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)


@app.route('/post/criar', methods=['GET', 'POST'])
@login_required
def criar_post():
    form = FormCriarPost()
    if form.validate_on_submit():
        post = Post(titulo=form.titulo.data, corpo=form.corpo.data, autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post Criado com Sucesso', 'alert-success')
        return redirect(url_for('forum'))
    return render_template('criarpost.html', form=form)


def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (400, 400)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo


@app.route('/perfil/editar', methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form = FormEditarPerfil()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        if form.foto_perfil.data:
            nome_imagem = salvar_imagem(form.foto_perfil.data)
            current_user.foto_perfil = nome_imagem

        database.session.commit()
        flash('Perfil atualizado com Sucesso', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == "GET":
        form.email.data = current_user.email
        form.username.data = current_user.username
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editarperfil.html', foto_perfil=foto_perfil, form=form)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = FormCriarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Post Atualizado com Sucesso', 'alert-success')
            return redirect(url_for('home'))
    else:
        form = None
    return render_template('post.html', post=post, form=form)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Post Excluído com Sucesso', 'alert-danger')
        return redirect(url_for('home'))
    else:
        abort(403)

@app.route('/forum')
def forum():
    posts = Post.query.order_by(Post.id.desc())
    return render_template('forum.html', posts=posts)
