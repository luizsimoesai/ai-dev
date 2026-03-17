from pedido.pedido import Pedido

# [S] Single Responsibility Principle:
#   Responsabilidade única: calcular o total de um pedido com entrega,
#   somando os itens mais a taxa de frete.
#
# [L] Liskov Substitution Principle:
#   PedidoDelivery também substitui Pedido sem quebrar nada — só acrescenta
#   o atributo taxa_entrega e inclui ele no total. O contrato de calcular_total
#   continua sendo respeitado: recebe os dados do pedido, retorna um número.
class PedidoDelivery(Pedido):
    def __init__(self, cliente, itens, taxa_entrega):
        super().__init__(cliente, itens)
        self.taxa_entrega = taxa_entrega

    def calcular_total(self):
        total = sum(item.preco for item in self.itens) + self.taxa_entrega
        return total