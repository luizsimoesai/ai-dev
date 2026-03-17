from abc import ABC, abstractmethod


# STRATEGY PATTERN — Interface da Estratégia (Strategy Interface)
#
# No padrão Strategy, definimos uma interface comum para todas as
# variações de um comportamento (aqui: formas de pagamento).
#
# Benefício: o código que usa o pagamento depende apenas desta
# interface, sem saber qual implementação concreta será usada.
# Isso permite trocar a estratégia em tempo de execução sem
# alterar quem a consome.
#
# [S] Single Responsibility Principle:
#   Esta classe tem UMA única responsabilidade: definir o contrato
#   que toda forma de pagamento deve seguir. Ela não processa nada,
#   não cria objetos, não loga — só estabelece o "o que deve existir".
#
# [L] Liskov Substitution Principle:
#   Qualquer subclasse de Pagamento (PagamentoPix, PagamentoCartao...)
#   pode substituir esta classe base sem quebrar o código que a usa.
#   Quem chama .processar() não precisa saber com qual subclasse está
#   falando — todas se comportam conforme o contrato definido aqui.
class Pagamento(ABC):
    @abstractmethod
    def processar(self, valor):
        # Cada estratégia concreta deve implementar este método
        # com sua própria lógica de processamento.
        pass
