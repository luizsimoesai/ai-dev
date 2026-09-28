from pagamento.pagamento import Pagamento


# STRATEGY PATTERN — Estratégia Concreta (Concrete Strategy)
#
# PagamentoCartao é uma das estratégias concretas do padrão Strategy.
# Ela implementa a interface Pagamento com a lógica específica
# de pagamento via cartão.
#
# [S] Single Responsibility Principle:
#   Esta classe tem UMA responsabilidade: processar pagamentos via cartão.
#   Ela não calcula totais de pedido, não cria outros objetos, não decide
#   qual meio de pagamento usar. Só sabe "como pagar de cartão".
#
# [O] Open/Closed Principle:
#   Se amanhã surgir PagamentoBoleto, você cria uma nova classe — sem
#   modificar PagamentoCartao nem nenhum outro código existente.
#   O sistema está aberto para extensão, fechado para modificação.
class PagamentoCartao(Pagamento):
    def processar(self, valor):
        # Implementação concreta da estratégia de cartão
        print(f"Processando pagamento de R$ {valor:.2f} via -Cartão-")
