from notificacao.notificacao import Notificacao


# [I] Interface Segregation Principle — na prática:
#   NotificacaoSMS também implementa apenas o que precisa.
#   Se no futuro SMS ganhar funcionalidades extras (ex: confirmar entrega),
#   o correto é criar uma interface nova — não engordar Notificacao e forçar
#   NotificacaoEmail a implementar algo que não faz sentido para ela.
class NotificacaoSMS(Notificacao):
    def enviar_notificacao(self, cliente, mensagem):
        print(f"Enviando SMS para {cliente.nome}: {mensagem}")