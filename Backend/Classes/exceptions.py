# Herdar de uma exceção padrão 
class ExcecaoTemplate(Exception):
    # Construtor
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception

    # Mensagem customizada
    def __str__(self):
        if self.original_exception:
            return f"{self.message} -> Causa: {str(self.original_exception)}"
        return self.message

#class Excecao_(ExcecaoTemplate):
#    def __init__(self, message="Erro em ", excecaoExterna = None):
#        super().__init__(message, excecaoExterna)