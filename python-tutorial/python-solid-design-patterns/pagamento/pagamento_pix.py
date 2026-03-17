from pagamento.pagamento import Pagamento


# STRATEGY PATTERN — Estratégia Concreta (Concrete Strategy)
#
# PagamentoPix é outra estratégia concreta. Ela implementa o mesmo
# contrato definido em Pagamento, mas com comportamento diferente.
#
# [S] Single Responsibility Principle:
#   Responsabilidade única: processar pagamentos via Pix. Nada mais.
#
# [O] Open/Closed Principle:
#   Esta classe foi adicionada sem modificar PagamentoCartao nem Pagamento.
#   É exatamente isso que O/C propõe: estender o sistema criando código novo,
#   não alterando o que já funciona.
#
# [L] Liskov Substitution Principle (melhor observado aqui na prática):
#   Em main.py, o código faz:
#       pagamento = PagamentoFactory.criar_pagamento("pix")  # retorna PagamentoPix
#       pagamento.processar(valor)
#   Mas poderia ser "cartao" e o resultado seria igualmente correto.
#   PagamentoPix substitui Pagamento sem surpresas — o contrato é respeitado.
class PagamentoPix(Pagamento):
    def processar(self, valor):
        # Implementação concreta da estratégia de Pix
        print(f"Processando pagamento de R$ {valor:.2f} via -Pix-")
