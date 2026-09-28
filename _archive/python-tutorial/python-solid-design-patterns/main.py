from cliente import Cliente
from item import Item

# from pedido.pedido_retirada import PedidoRetirada
from pedido.pedido_delivery import PedidoDelivery
# from pagamento.pagamento_cartao import PagamentoCartao
# from pagamento.pagamento_pix import PagamentoPix
from pagamento.pagamento_factory import PagamentoFactory
# from notificacao.notificacao_email import NotificacaoEmail
# from notificacao.notificacao_sms import NotificacaoSMS
from notificacao.notificacao_facade import NotificacaoFacade
from observador.observador_status import ObservadorStatus


cliente = Cliente("Luiz", "Home")
print("\n--- CLIENTE ---")
print(f"# Nome: {cliente.nome} - Endereço: {cliente.endereco}")

item_um = Item("Pizza", 30.0)
item_dois = Item("Refrigerante", 5.0)
print("\n--- PEDIDO ---")
print(f"Item: {item_um.nome}, Preço: {item_um.preco}")
print(f"Item: {item_dois.nome}, Preço: {item_dois.preco}")

# itens e taxa de entrega
itens = [item_um, item_dois]
taxa_entrega=7.00

# pedido_retirada = PedidoRetirada(cliente, itens)
# print(f"Preço do Pedido -Retirada-: {pedido_retirada.calcular_total():.2f}")

# pedido_delivery = PedidoDelivery(cliente, itens, taxa_entrega)
# print(f"Preço do Pedido -Delivery-: {pedido_delivery.calcular_total():.2f}")

pedido = PedidoDelivery(cliente, itens, taxa_entrega)
valor_pedido = pedido.calcular_total()
print("\n--- TOTAL ---")
print(f"Preço do Pedido -Delivery-: {pedido.calcular_total():.2f}")

# pagamento_cartao = PagamentoCartao()
# pagamento_pix = PagamentoPix()
# pagamento_cartao.processar(valor_pedido)
# pagamento_pix.processar(valor_pedido)

tipo_pagamento = "pix"
pagamento = PagamentoFactory.criar_pagamento(tipo_pagamento).processar(valor_pedido)


# MENSAGEM = "Seu pedido saiu para entrega!"
# notificacao_email = NotificacaoEmail().enviar_notificacao(cliente, MENSAGEM)
# notificacao_sms = NotificacaoSMS().enviar_notificacao(cliente, MENSAGEM)
# notificacoes = NotificacaoFacade().enviar_notificacoes(cliente, MENSAGEM)

# pedido.status = "Pedido Confirmado!"
# notificacoes = NotificacaoFacade().enviar_notificacoes(cliente, pedido.status)

MENSAGEM_PAGO = "O pagamento foi confirmado!"
MENSAGEM_PREPARANDO = "O pedido está sendo preparado!"
MENSAGEM_ENVIADO = "O pedido saiu para entrega!"

notificacoes = NotificacaoFacade()
observador = ObservadorStatus(notificacoes)
pedido.adicionar_observadores(observador)

pedido.status = MENSAGEM_PAGO
pedido.status = MENSAGEM_PREPARANDO
pedido.status = MENSAGEM_ENVIADO


