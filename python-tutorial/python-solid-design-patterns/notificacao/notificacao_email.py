from notificacao.notificacao import Notificacao


# [I] Interface Segregation Principle — na prática:
#   NotificacaoEmail implementa APENAS enviar_notificacao().
#   Ela não foi obrigada a implementar nenhum método que não faz sentido
#   para e-mail — porque a interface Notificacao é enxuta o suficiente.
class NotificacaoEmail(Notificacao):
    def enviar_notificacao(self, cliente, mensagem):
        print(f"Enviando e-mail para {cliente.nome}: {mensagem}")
        