import entity.Servidor as Servidor
from mysql.connector import Error

class controllerServidor:
    def __init__(self):
        pass

    def insereServidor(self, nome, cpf, email, senha, conector):

        try:
            if conector.is_connected():
                cursor = conector.cursor()

                sql_query = "insert into servidores(nome, cpf, email, senha) values(%s, %s, %s, %s)"
                valores = (nome, cpf, email, senha)

                cursor.execute(sql_query, valores)
                conector.commit()

                print("Inserido")
        except Error as e:
            print(e)

    def imprimeServidor(self, cpf, conector):
        try:
            if conector.is_connected():
                cursor = conector.cursor()

                if cpf == '':
                    sql_query = "select*from servidores"
                    cursor.execute(sql_query)
                else:    
                    sql_query = "select*from servidores where cpf = %s"
                    valores = ([cpf])
                    cursor.execute(sql_query, valores)

                resultados = cursor.fetchall()

                for r in resultados:
                    print(r)

        except Error as e:
            print(e)