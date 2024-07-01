from flask import Flask, render_template, request, redirect, url_for, flash, session
import entity.controllerCliente as controllerCliente
import entity.controllerServidor as controllerServidor
import mysql.connector
from mysql.connector import Error
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def create_connection():
    try:
        connection = mysql.connector.connect(
        host="localhost",
        user = "elias",
        password = "elias",
        database = "general_services"
    )
        if connection.is_connected():
            print("Conectado ao MySQL")
            return connection
    except Error as e:
        print("Erro ao conectar ao MySQL", e)
        return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        connection = create_connection()
        if connection is not None:
            cursor = connection.cursor(dictionary=True)
            try:
                # Verificar se o usuário é um cliente
                cursor.execute("SELECT * FROM clientes WHERE email = %s AND senha = %s", (email, password))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user['id']
                    session['role'] = 'cliente'
                    flash('Login realizado com sucesso!', 'success')
                    return redirect(url_for('home_cliente'))
                
                # Verificar se o usuário é um servidor
                cursor.execute("SELECT * FROM servidores WHERE email = %s AND senha = %s", (email, password))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user['id']
                    session['role'] = 'servidor'
                    flash('Login realizado com sucesso!', 'success')
                    return redirect(url_for('home_servidor'))
                
                flash('E-mail ou senha incorretos.', 'danger')
            except Error as e:
                flash('Erro ao realizar login. Tente novamente.', 'danger')
                print("Erro ao verificar dados no MySQL", e)
            finally:
                cursor.close()
                connection.close()
        else:
            flash('Erro ao conectar ao banco de dados.', 'danger')
    
    return render_template('login.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        cpf = request.form['cpf']
        password = request.form['password']
        role = request.form['role']

        connection = create_connection()

        cCliente = controllerCliente.controllerCliente()
        cServidor = controllerServidor.controllerServidor()

        if connection is not None:
            #cursor = connection.cursor()
            print("Conexão estabelecida com sucesso")
            try:
                if role == 'cliente':
                    cCliente.insereCliente(nome, cpf, email, password, connection)
                    print("Cliente inserido")
                    
                    #sql = "INSERT INTO clientes (nome, contato) VALUES (%s, %s)"
                    #cursor.execute(sql, (nome, email))
                elif role == 'servidor':
                    cServidor.insereServidor(nome, cpf, email, password, connection)
                    #sql = "INSERT INTO servidores (nome) VALUES (%s)"
                    #cursor.execute(sql, (nome,))
                    #id_servidor = cursor.lastrowid
                    # Aqui você pode adicionar a lógica para vincular os serviços ao servidor
                connection.commit()
                flash('Cadastro realizado com sucesso!', 'success')
            except Error as e:
                connection.rollback()
                flash('Erro ao cadastrar. Tente novamente.', 'danger')
                print("Erro ao inserir dados no MySQL", e)
            finally:
                connection.close()
        
        return redirect(url_for('cadastro'))

    return render_template('cadastro.html')

@app.route('/home_servidor', methods=['GET', 'POST']) 
def home_servidor():
    if request.method == 'POST':
        if 'user_id' not in session or session.get('role') != 'servidor':
            flash('Usuário não autorizado')
            return redirect(url_for('home_servidor'))

        nome_servico = request.form['nome_servico']
        valor_servico = request.form['valor_servico']

        connection = create_connection()
        if connection is not None:
            cursor = connection.cursor()
            try:
                sql = "INSERT INTO servicos (nome, preco) VALUES (%s, %s)"
                cursor.execute(sql, (nome_servico, valor_servico))
                sql = "INSERT INTO servidores_servicos (id_servidor, id_servico) VALUES (%s, %s)"
                cursor.execute(sql, (session['user_id'], cursor.lastrowid))
                connection.commit()
                flash('Serviço adicionado com sucesso!')
            except Error as e:
                connection.rollback()
                print("Erro ao inserir dados no MySQL", e)
                flash('Erro ao adicionar serviço.')
            finally:
                cursor.close()
                connection.close()

        return redirect(url_for('home_servidor'))

    connection = create_connection()
    servicos = []
    if connection is not None:
        cursor = connection.cursor(dictionary=True)
        try:
            sql = "SELECT sv.nome, sv.preco FROM servicos sv, servidores s, servidores_servicos ss WHERE ss.id_servico = sv.id and ss.id_servidor = s.id and s.id = %s;"
            cursor.execute(sql, (session['user_id'],))
            servicos = cursor.fetchall()
        except Error as e:
            print("Erro ao buscar dados no MySQL", e)
        finally:
            cursor.close()
            connection.close()

    return render_template('home_servidor.html', current_url=request.path, servicos=servicos)

@app.route('/home_cliente', methods=['GET', 'POST'])
def home_cliente():
    if 'user_id' not in session or session.get('role') != 'cliente':
        flash('Usuário não autorizado')
        return redirect(url_for('login'))

    search_query = request.form.get('search_query', '')

    connection = create_connection()
    servicos = []
    if connection is not None:
        cursor = connection.cursor(dictionary=True)
        try:
            if search_query:
                sql = """
                SELECT sv.nome AS servico_nome, sv.preco, s.nome AS servidor_nome, s.email,
                sv.id AS servico_id, s.id AS servidor_id
                FROM servicos sv
                JOIN servidores_servicos ss ON sv.id = ss.id_servico
                JOIN servidores s ON s.id = ss.id_servidor
                WHERE sv.nome LIKE %s
                """
                cursor.execute(sql, ('%' + search_query + '%',))
            else:
                sql = """
                SELECT sv.nome AS servico_nome, sv.preco, s.nome AS servidor_nome, s.email,
                sv.id AS servico_id, s.id AS servidor_id
                FROM servicos sv
                JOIN servidores_servicos ss ON sv.id = ss.id_servico
                JOIN servidores s ON s.id = ss.id_servidor
                """
                cursor.execute(sql)
            servicos = cursor.fetchall()
        except Error as e:
            print("Erro ao buscar dados no MySQL", e)
        finally:
            cursor.close()
            connection.close()

    return render_template('home_cliente.html', current_url=request.path, servicos=servicos, search_query=search_query)


@app.route('/contratar', methods=['GET', 'POST'])
def contratar():
    if request.method == 'POST': 
        id_servidor = request.form.get('id_servidor')
        id_servico = request.form.get('id_servico')
        id_cliente = request.form.get('id_cliente')
        data_hora = request.form.get('data_agendamento')  # Supondo que você adicione um campo de data em algum lugar

        connection = create_connection()
        if connection is not None:
            cursor = connection.cursor()
            try:
                # Verifique se a data está disponível
                check_sql = "SELECT COUNT(*) FROM agenda_servidores WHERE id_servidor = %s AND data_hora = %s"
                cursor.execute(check_sql, (id_servidor, data_hora))
                (count,) = cursor.fetchone()

                if count > 0:
                    flash('Data não disponível para este servidor.')
                else:
                    # Insira o agendamento no banco de dados
                    insert_agendamento_sql = "INSERT INTO agendamentos (id_cliente, id_servidor, id_servico, data_hora) VALUES (%s, %s, %s, %s)"
                    cursor.execute(insert_agendamento_sql, (id_cliente, id_servidor, id_servico, data_hora))
                    
                    insert_agenda_servidores_sql = "INSERT INTO agenda_servidores (id_servidor, data_hora, disponivel) VALUES (%s, %s, 0)"
                    cursor.execute(insert_agenda_servidores_sql, (id_servidor, data_hora))
                    
                    insert_clientes_servicos_sql = "INSERT INTO clientes_servicos (id_cliente, id_servico) VALUES (%s, %s)"
                    cursor.execute(insert_clientes_servicos_sql, (id_cliente, id_servico))
                    
                    connection.commit()
                    flash('Agendamento realizado com sucesso!')
            except Error as e:
                connection.rollback()
                flash('Erro ao realizar agendamento.')
                print("Erro ao inserir agendamento no MySQL", e)
            finally:
                cursor.close()
                connection.close()
 
        return redirect(url_for('home_cliente'))

    if request.method == 'GET':
        id_servidor = request.args.get('id_servidor')
        id_servico = request.args.get('id_servico')
        id_cliente = request.args.get('id_cliente')
        
        if not all([id_servidor, id_servico, id_cliente]):
            flash('Erro: Parâmetros insuficientes.')
            return redirect(url_for('home_cliente'))
        
        connection = create_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT data_hora FROM agenda_servidores WHERE id_servidor = %s", (id_servidor,))
        unavailable_dates = [row[0].strftime('%Y-%m-%d') for row in cursor.fetchall()]
        cursor.close()
        connection.close()

        return render_template('contratar.html', id_cliente=id_cliente, id_servidor=id_servidor, id_servico=id_servico, unavailable_dates=unavailable_dates)
    return render_template('contratar.html')

@app.route('/agenda')
def agenda():
    user_id = session['user_id']
    user_type = session.get('role')  # Assume que você tem isso na sessão (cliente ou servidor)
    
    connection = create_connection()
    agendamentos = []
    
    if connection is not None:
        cursor = connection.cursor()
        try:
            if user_type == 'cliente':
                sql = """
                SELECT a.data_hora, s.nome, sv.nome AS servidor_nome, sv.email, sv.id AS servidor_id, s.id AS servico_id, a.id_cliente AS cliente_id
                FROM agendamentos a
                JOIN servicos s ON a.id_servico = s.id
                JOIN servidores sv ON a.id_servidor = sv.id
                WHERE a.id_cliente = %s
                """
                cursor.execute(sql, (user_id,))
            elif user_type == 'servidor':
                sql = """ 
                SELECT a.data_hora, s.nome, c.nome AS cliente_nome, c.email, a.id_servidor AS servidor_id, s.id AS servico_id, a.id_cliente AS cliente_id
                FROM agendamentos a
                JOIN servicos s ON a.id_servico = s.id
                JOIN clientes c ON a.id_cliente = c.id
                WHERE a.id_servidor = %s 
                """ 
                cursor.execute(sql, (user_id,))
                
            agendamentos = cursor.fetchall()
        except Error as e:
            flash('Erro ao buscar agendamentos.')
            print("Erro ao buscar agendamentos no MySQL", e)
        finally:
            cursor.close() 
            connection.close() 
    
    return render_template('agenda.html', agendamentos=agendamentos, user_type=user_type)
 
@app.route('/excluir_agendamento', methods=['POST'])
def excluir_agendamento():
    servico = request.form.get('servico')
    print("Excluindo agendamento")
    print(servico)
    #editar string para pegar a data 
    servico = servico.strip("()")
    servico = servico.replace("datetime.date(", "")
    servico = servico.replace("'", "")
    servico = servico.replace(" ", "")
    servico = servico.replace(")", "")
    servico = servico.split(",")
    servico[1] = int(servico[1])
    servico[2] = int(servico[2])
    if(servico[1] < 10):
        servico[1] = "0" + str(servico[1])
    else:
        servico[1] = str(servico[1])
    if(servico[2] < 10):
        servico[2] = "0" + str(servico[2])
    else:
        servico[2] = str(servico[2])
    data_formatada = servico[0] + "-" + servico[1] + "-" + servico[2]
    print(servico)
    print(data_formatada) 
    print(servico[0], servico[1], servico[2], servico[3], servico[4], servico[5], servico[6], servico[7], servico[8])

    connection = create_connection()
    if connection is not None:
        cursor = connection.cursor() 
        try:
            # Exclua das tabelas relacionadas
            cursor.execute("DELETE FROM clientes_servicos WHERE id_cliente = %s AND id_servico = %s;", (servico[8], servico[7]))
            cursor.execute("DELETE FROM agenda_servidores WHERE id_servidor = %s AND data_hora = %s", (servico[6], data_formatada))
            cursor.execute("DELETE FROM agendamentos WHERE id_cliente = %s AND id_servico = %s AND data_hora = %s", (servico[8], servico[7], data_formatada))
 
            connection.commit()
            flash('Agendamento excluído com sucesso!')
        except Error as e:
            connection.rollback()
            flash('Erro ao excluir agendamento.')
            print("Erro ao excluir agendamento no MySQL", e)
        finally:
            cursor.close()
            connection.close() 

    return redirect(url_for('agenda'))

if __name__ == '__main__':
    app.run(debug=True)
