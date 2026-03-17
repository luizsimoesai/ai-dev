from pagamento.pagamento_pix import PagamentoPix
from pagamento.pagamento_cartao import PagamentoCartao

# =============================================================================
# PADRÃO DE PROJETO: FACTORY METHOD (Fábrica)
# =============================================================================
# [S] Single Responsibility Principle:
#   Esta classe tem UMA responsabilidade: saber como criar objetos de pagamento.
#   Ela não processa pagamentos, não conhece regras de negócio — só instancia.
#
# =============================================================================
# Problema que resolve:
#   Quem chama o código não precisa saber COMO criar o objeto certo —
#   só precisa dizer O QUE quer ("pix", "cartao").
#   Sem a Factory, o main.py precisaria fazer:
#       if tipo == "pix": pagamento = PagamentoPix()
#       elif tipo == "cartao": pagamento = PagamentoCartao()
#   Esse if ficaria espalhado por todo o sistema.
#
# Solução:
#   Centraliza a lógica de criação em um único lugar.
#   Se amanhã surgir PagamentoBoleto, você adiciona aqui — e só aqui.
#
# Princípio SOLID relacionado:
#   Open/Closed Principle — aberto para extensão (novo tipo),
#   fechado para modificação (quem usa não muda).
# =============================================================================


class PagamentoFactory:

    @staticmethod
    def criar_pagamento(tipo):
        # O método recebe uma string simples e devolve o objeto correto.
        # O chamador trabalha com a interface Pagamento sem conhecer
        # as classes concretas PagamentoPix ou PagamentoCartao.
        if tipo == "pix":
            return PagamentoPix()
        elif tipo == "cartao":
            return PagamentoCartao()
        else:
            # Falha explícita: melhor lançar um erro claro do que
            # retornar None e causar um AttributeError misterioso mais tarde.
            raise ValueError(f"Tipo de pagamento '{tipo}' não suportado.")
