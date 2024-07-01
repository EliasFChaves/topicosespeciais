class Servidor:
    def __init__(self, nome, cpf, celular, email, senha):
        self.nome = nome
        self.cpf = cpf
        self.celular = celular
        self.email = email
        self.senha = senha

    @property
    def getNome(self):
        return self.nome
    
    def nome(self, nome):
        self.nome = nome

    @property
    def getCpf(self):
        return self.cpf
    
    def cpf(self, cpf):
        self.cpf = cpf

    @property
    def getCelular(self):
        return self.celular
    
    def celular(self, celular):
        self.celular = celular

    @property
    def getEmail(self):
        return self.email
    
    def email(self, email):
        self.email = email
    
    @property
    def getSenha(self):
        return self.senha
    
    def senha(self, senha):
        self.senha = senha
    
    
    

    








