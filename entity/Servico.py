#the service class must receive a worker in its constructor
import entity.Servico as Servico


class Servico:
    def __init__(self, nome, preco):
        self.nome = nome
        self.preco = preco
    
    @property
    def getNome(self):
        return self.nome
    
    def nome(self, nome):
        self.nome = nome

    @property
    def getPreco(self):
        return self.preco
    
    def preco(self, preco):
        self.preco = preco
    