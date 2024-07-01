import entity.Cliente as Cliente
from mysql.connector import Error

class controllerServico:
    def __init__(self):
        pass

    def insereServico(self, nome, preco, conector):

        try:
            if conector.is_connected():
                cursor = conector.cursor()

                sql_query = "insert into servicos(nome, preco) values(%s, %s)"
                valores = (nome, preco)

                cursor.execute(sql_query, valores)
                conector.commit()

                print("Inserido")
        except Error as e:
            print(e)

    def imprimeServico(self, nome, conector):
        try:
            if conector.is_connected():
                cursor = conector.cursor()

                if nome == '':
                    sql_query = "select*from servicos"
                    cursor.execute(sql_query)
                else:    
                    sql_query = "select*from clientes where nome = %s"
                    valores = ([nome])
                    cursor.execute(sql_query, valores)

                resultados = cursor.fetchall()

                for r in resultados:
                    print(r)

        except Error as e:
            print(e)
    
    def insereServidorServico(self, id_servidor, id_servico, conector):

        try:
            if conector.is_connected():
                cursor = conector.cursor()

                sql_query = "insert into servidores_servicos(id_servidor, id_servico) values(%s, %s)"
                valores = (id_servidor, id_servico)

                cursor.execute(sql_query, valores)
                conector.commit()

                print("Inserido")
        except Error as e:
            print(e)