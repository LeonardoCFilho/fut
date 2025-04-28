# Herdar de uma exceção padrão 
class ExcecaoTemplate(Exception):
    # Construtor
    def __init__(self, message, excecaoExterna = None):
        super().__init__(message)
        self.message = message
        self.excecaoExterna = excecaoExterna
    
    # Mensagem de erro customizada
    def __str__(self):
        if self.excecaoExterna:
            return f"{super().__str__()} (Causado por: {str(self.excecaoExterna)})"
        return super().__str__()
        
# Exceção para cada classe criada, mensagem já tem valor padrão
class Excecao_ExecutorTestes(ExcecaoTemplate):
    def __init__(self, message="Erro em ExecutorTestes", excecaoExterna = None):
        super().__init__(message, excecaoExterna)

class Excecao_GeradorRelatorios(ExcecaoTemplate):
    def __init__(self, message="Erro em GeradorRelatorios", excecaoExterna = None):
        super().__init__(message, excecaoExterna)

# Menos relevante
class Excecao_GerenciadorTestes(ExcecaoTemplate):
    def __init__(self, message="Erro em GerenciadorTestes", excecaoExterna = None):
        super().__init__(message, excecaoExterna)

class Excecao_GerenciadorValidator(ExcecaoTemplate):
    def __init__(self, message="Erro em GerenciadorValidator", excecaoExterna = None):
        super().__init__(message, excecaoExterna)

class Excecao_InicializadorSistema(ExcecaoTemplate):
    def __init__(self, message="Erro em InicializadorSistema", excecaoExterna = None):
        super().__init__(message, excecaoExterna)

#class Excecao_(ExcecaoTemplate):
#    def __init__(self, message="Erro em ", excecaoExterna = None):
#        super().__init__(message, excecaoExterna)