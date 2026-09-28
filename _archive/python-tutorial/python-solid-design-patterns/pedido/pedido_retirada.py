from pedido.pedido import Pedido

# [S] Single Responsibility Principle:
#   Esta classe tem uma única responsabilidade: calcular o total de um pedido
#   de retirada (sem frete). Nada mais.
#
# [L] Liskov Substitution Principle:
#   PedidoRetirada pode substituir Pedido em qualquer lugar do código.
#   Ela honra o contrato: recebe cliente e itens, e retorna um total numérico.
class PedidoRetirada(Pedido):
    def calcular_total(self):
        return sum(item.preco for item in self.itens)