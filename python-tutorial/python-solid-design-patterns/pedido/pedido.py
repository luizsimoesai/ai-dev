# TEMPLATE METHOD PATTERN
#
# O padrão Template Method define o "esqueleto" de um algoritmo em uma classe
# base (abstrata), deixando alguns passos para as subclasses implementarem.
#
# PROBLEMA que resolve:
#   Você tem vários tipos de pedido (ex: delivery, balcão, agendado) que seguem
#   o mesmo fluxo geral, mas diferem em algum passo específico — como calcular
#   o total (com frete, sem frete, com desconto, etc.).
#   Sem esse padrão, você repetiria a estrutura do algoritmo em cada subclasse.
#
# SOLUÇÃO:
#   A classe base define o método "template" (o fluxo geral) e delega os passos
#   variáveis para métodos abstratos que cada subclasse vai implementar.
#
# PARTICIPANTES:
#   - Classe abstrata (Pedido): define a estrutura comum e os métodos abstratos.
#   - Subclasses concretas: implementam apenas os passos que variam.
#
# [S] Single Responsibility Principle:
#   Pedido é responsável apenas por definir o contrato base de um pedido
#   (cliente, itens, e a obrigação de saber calcular o total).
#   Ela não decide como calcular — isso é responsabilidade das subclasses.
#
# [O] Open/Closed Principle:
#   Para adicionar um novo tipo de pedido (ex: PedidoAgendado), basta criar
#   uma nova subclasse — sem tocar em Pedido, PedidoDelivery ou PedidoRetirada.
#
# [D] Dependency Inversion Principle:
#   O código de alto nível (main.py) não depende de PedidoDelivery nem de
#   PedidoRetirada diretamente para operar — ele depende da abstração Pedido.
#   Exemplo: pedido_delivery.status = "Confirmado!" funciona porque main.py
#   está falando com o contrato de Pedido, não com detalhes da subclasse.
#   Se amanhã o status precisar ser notificado, logado ou persistido, a mudança
#   fica aqui — quem usa não precisa saber.

from abc import ABC, abstractmethod

# Classe abstrata — define o contrato e a estrutura do algoritmo.
# Nenhuma instância direta de Pedido pode ser criada; só das subclasses.
class Pedido(ABC):
    def __init__(self, cliente, itens):
        self.cliente = cliente
        self.itens = itens
        # O status é inicializado aqui, na base, pois é um comportamento
        # compartilhado por todos os tipos de pedido.
        self._status = "Pedido criado!"
        self.observadores = []

    # PROPERTY — Encapsulamento do atributo _status
    #
    # O atributo real é _status (prefixo _ indica "uso interno").
    # A @property expõe uma interface pública limpa: pedido.status
    # sem que quem lê precise saber que o dado se chama _status internamente.
    @property
    def status(self):
        return self._status

    # SETTER — Lógica ao atribuir um novo valor
    #
    # Ao fazer pedido.status = "Confirmado!", o Python chama este método
    # automaticamente, em vez de atribuir o valor direto ao atributo.
    # Isso nos permite executar lógica adicional na atribuição — aqui,
    # um print — sem que quem usa precise chamar nenhum método especial.
    # Se amanhã precisarmos salvar no banco ou enviar evento, é só adicionar
    # aqui, sem mudar nenhuma linha de quem usa o status.
    @status.setter
    def status(self, novo_status):
        self._status = novo_status
        # Sempre que o status muda, todos os observadores registrados
        # são avisados automaticamente. Pedido não sabe o que cada um
        # vai fazer com essa informação — só avisa que algo mudou.
        self.notificar_observadores()

    # OBSERVER PATTERN — O "Sujeito" (Subject / Observable)
    #
    # Pedido é o objeto observado. Ele mantém uma lista de observadores
    # interessados em saber quando algo nele muda (aqui: o status).
    #
    # PROBLEMA que resolve:
    #   Antes, ao mudar o status, Pedido precisaria chamar diretamente:
    #       NotificacaoFacade().enviar_notificacoes(...)
    #   Isso cria acoplamento direto: Pedido passa a depender de quem notifica.
    #   E se amanhã quisermos também logar, auditar ou salvar no banco?
    #   Teríamos que modificar Pedido a cada novo comportamento.
    #
    # SOLUÇÃO:
    #   Pedido não sabe quem está ouvindo — ele só mantém uma lista e avisa.
    #   Cada observador decide o que fazer quando é notificado.
    #   Para adicionar um novo comportamento (ex: salvar log), basta criar
    #   um novo observador e registrá-lo — sem tocar em Pedido.
    #
    # PARTICIPANTES neste arquivo:
    #   - Sujeito (Subject): Pedido — mantém a lista e notifica
    #   - Observador (Observer): qualquer objeto com método .atualizar(pedido)

    def adicionar_observadores(self, observador):
        # Registra um novo observador na lista.
        # Pedido não sabe o tipo concreto — só exige que tenha .atualizar().
        self.observadores.append(observador)

    def notificar_observadores(self):
        # Percorre todos os observadores registrados e avisa cada um.
        # O argumento `self` passa o próprio pedido, para que o observador
        # possa acessar qualquer dado que precisar (status, cliente, etc.).
        for observador in self.observadores:
            observador.atualizar(self)


    # Método abstrato — cada subclasse DEVE implementar sua própria lógica
    # de cálculo de total. É aqui que o comportamento varia entre os tipos
    # de pedido (ex: PedidoDelivery inclui frete, PedidoBalcao não).
    @abstractmethod
    def calcular_total(self):
        pass