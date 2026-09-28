# OBSERVER PATTERN — O "Observador" (Observer / Listener)
#
# ANALOGIA:
#   Pense em uma newsletter: o site (Sujeito) não liga para cada assinante
#   manualmente — ele só dispara o evento "nova publicação" e todos os
#   assinantes (Observadores) recebem automaticamente.
#   Aqui: Pedido é o site, ObservadorStatus é o assinante.
#
# FLUXO COMPLETO neste projeto:
#   1. main.py cria o pedido e registra o observador:
#          observador = ObservadorStatus(notificacoes)
#          pedido.adicionar_observadores(observador)
#
#   2. main.py muda o status:
#          pedido.status = "Pedido Confirmado!"
#
#   3. O setter de Pedido chama automaticamente:
#          self.notificar_observadores()
#
#   4. Pedido chama para cada observador registrado:
#          observador.atualizar(self)   ← self = o próprio pedido
#
#   5. ObservadorStatus recebe o pedido, monta a mensagem e
#      delega o envio para a NotificacaoFacade:
#          notificacoes.enviar_notificacoes(pedido.cliente, mensagem)
#
# BENEFÍCIO CHAVE (Open/Closed + Dependency Inversion):
#   Pedido nunca importou NotificacaoFacade. Ele não sabe que notificações
#   existem. Se amanhã quisermos também salvar um log em arquivo, criamos
#   ObservadorLog e registramos junto — zero mudanças em Pedido.
class ObservadorStatus:
    def __init__(self, notificacoes):
        # Recebe a facade de notificações por injeção de dependência.
        # ObservadorStatus depende da abstração "algo que envia notificações",
        # não de Email ou SMS diretamente — isso é o [D] do SOLID na prática.
        self.notificacoes = notificacoes

    def atualizar(self, pedido):
        # Este método é o "gancho" que Pedido chama quando algo muda.
        # pedido.status já contém o novo valor (o setter atualizou antes de notificar).
        # pedido.cliente fornece o destinatário da notificação.
        mensagem = f"O status do pedido foi atualizado para '{pedido.status}'"
        self.notificacoes.enviar_notificacoes(pedido.cliente, mensagem)