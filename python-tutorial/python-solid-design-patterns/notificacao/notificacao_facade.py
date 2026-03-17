from notificacao.notificacao_email import NotificacaoEmail
from notificacao.notificacao_sms import NotificacaoSMS


# FACADE PATTERN — Fachada
#
# PROBLEMA que resolve:
#   O código cliente (main.py) não deveria precisar saber que existem
#   múltiplos canais de notificação, instanciá-los um a um e chamar
#   cada um separadamente. Isso espalharia a complexidade por todo o sistema.
#
# SOLUÇÃO — A Fachada:
#   NotificacaoFacade é uma interface simplificada que esconde a complexidade
#   de coordenar vários subsistemas (Email, SMS, e futuramente Push, WhatsApp...).
#
#   Antes (sem Facade) — main.py precisava conhecer cada canal:
#       NotificacaoEmail().enviar_notificacao(cliente, msg)
#       NotificacaoSMS().enviar_notificacao(cliente, msg)
#
#   Depois (com Facade) — main.py só conhece a fachada:
#       NotificacaoFacade().enviar_notificacoes(cliente, msg)
#
# BENEFÍCIOS:
#   - O cliente depende de uma interface simples, não dos detalhes internos.
#   - Para adicionar WhatsApp, só muda aqui — main.py não precisa saber.
#   - Reduz o acoplamento entre quem usa e quem implementa as notificações.
#
# ANALOGIA:
#   A fachada é como o balcão de uma loja: você pede "quero um sanduíche"
#   sem saber (ou precisar saber) quem vai assar o pão, montar e embrulhar.
class NotificacaoFacade:
    def __init__(self):
        # A Facade conhece e gerencia os subsistemas internamente.
        # O cliente nunca precisa instanciar ou conhecer essas classes.
        self.notificacoes = [NotificacaoEmail(), NotificacaoSMS()]

    def enviar_notificacoes(self, cliente, mensagem):
        # Ponto de entrada único: coordena todos os canais de notificação.
        # Adicionar um novo canal = adicionar à lista aqui, nada mais.
        for notificacao in self.notificacoes:
            notificacao.enviar_notificacao(cliente, mensagem)