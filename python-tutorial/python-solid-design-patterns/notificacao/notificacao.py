from abc import ABC, abstractmethod


# [I] Interface Segregation Principle — Princípio da Segregação de Interface
#
# PROBLEMA que o "I" resolve:
#   Imagine uma interface grande com vários métodos: enviar_email(),
#   enviar_sms(), enviar_push(), registrar_log()...
#   Uma classe que só envia SMS seria forçada a implementar enviar_email()
#   mesmo sem precisar — isso é uma dependência que ela não pediu.
#
# SOLUÇÃO:
#   Interfaces pequenas e focadas. Cada classe implementa apenas o que usa.
#   Aqui, Notificacao tem um único método: enviar_notificacao().
#   NotificacaoEmail e NotificacaoSMS implementam exatamente isso — nada mais.
#
# REGRA PRÁTICA:
#   "Nenhuma classe deve ser forçada a depender de métodos que não usa."
#   Se você perceber que uma subclasse está implementando um método só para
#   lançar NotImplementedError ou deixar vazio — é sinal que a interface
#   está grande demais e precisa ser quebrada em interfaces menores.
class Notificacao(ABC):
    @abstractmethod
    def enviar_notificacao(self, cliente, mensagem):
        # Contrato mínimo e focado: qualquer canal de notificação
        # precisa saber enviar uma mensagem para um cliente.
        pass
