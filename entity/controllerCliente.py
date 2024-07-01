import entity.Cliente as Cliente
from mysql.connector import Error

class controllerCliente:
    def __init__(self):
        pass

    def insereCliente(self, nome, cpf, email, senha, conector):

        try:
            if conector.is_connected():
                cursor = conector.cursor()

                sql_query = "insert into clientes(nome, cpf, email, senha) values(%s, %s, %s, %s)"
                valores = (nome, cpf, email, senha)

                cursor.execute(sql_query, valores)
                conector.commit()

                print("Inserido")
        except Error as e:
            print(e)

    def imprimeCliente(self, cpf, conector):
        try:
            if conector.is_connected():
                cursor = conector.cursor()

                if cpf == '':
                    sql_query = "select*from clientes"
                    cursor.execute(sql_query)
                else:    
                    sql_query = "select*from clientes where cpf = %s"
                    valores = ([cpf])
                    cursor.execute(sql_query, valores)

                resultados = cursor.fetchall()

                for r in resultados:
                    print(r)

        except Error as e:
            print(e)
    