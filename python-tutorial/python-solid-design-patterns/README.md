# **Sistema de Gerenciamento de Pedidos**

## **Descrição**

Este projeto implementa um sistema de gerenciamento de pedidos que simula um fluxo de pedidos de clientes, incluindo cálculo de totais, notificações, pagamento e atualização de status.

---

## **Funcionalidades**

- **Cadastro de Clientes e Itens**: Gerencia informações de clientes e produtos.
- **Gestão de Pedidos**: Suporte a pedidos para delivery e retirada.
- **Sistema de Pagamento**: Simulação de processamento de pagamentos.
- **Notificações**: Envio de notificações por e-mail e SMS.
- **Atualização de Status**: Rastreamento e notificação do status do pedido.
---

## **Tecnologias Utilizadas**

- **Python 3.10+**
- Design Patterns: _Factory Method, Template, Strategy, Facade, Observer_.
- Princípios **SOLID**.

---

## **Estrutura do Projeto**

```
.
├── cliente.py
├── item.py
├── main.py
├── notificacao/
│   ├── notificacao.py
│   ├── notificacao_email.py
│   ├── notificacao_sms.py
│   └── notificacao_facade.py
├── observador/
│   └── observador_status.py
├── pagamento/
│   ├── pagamento.py
│   ├── pagamento_cartao.py
│   └── pagamento_pix.py
├── pedido/
│   ├── pedido.py
│   ├── pedido_delivery.py
│   └── pedido_retirada.py
└── README.md
```

---

## **Como Executar**

1. Acesse o arquivo `main.py`.
2. Execute o programa:
   ```bash
   python main.py
   ```

---

## **Exemplo de Uso**

- **Cadastrar Cliente e Itens**:
  Crie um cliente e adicione itens ao pedido.
- **Criar Pedido**:
  Escolha entre _delivery_ ou _retirada_.
- **Efetuar Pagamento**:
  Simule pagamentos via Pix ou Cartão.
- **Receber Notificações**:
  Clientes recebem notificações do status do pedido.

---

## **SOLID**

O acrônimo SOLID representa os cinco princípios que facilitam o processo de desenvolvimento — o que facilita a manutenção e a expansão do software.

Estes princípios são fundamentais na programação orientada a objetos e podem ser aplicados em qualquer linguagem que adote este paradigma.

Os 5 princípios são:

**S** — Single Responsibility Principle (Princípio da responsabilidade única)  
**O** — Open-Closed Principle (Princípio Aberto-Fechado)  
**L** — Liskov Substitution Principle (Princípio da substituição de Liskov)  
**I** — Interface Segregation Principle (Princípio da Segregação da Interface)  
**D** — Dependency Inversion Principle (Princípio da inversão da dependência)  

## Padrões de Projeto - Design Patterns

- https://refactoring.guru/pt-br/design-patterns/python
- **Template Method** — define o esqueleto de um algoritmo na classe base e deixa as subclasses preencherem os passos variáveis via herança.
- **Strategy** — define uma família de algoritmos em classes separadas e os torna intercambiáveis via composição.
- **Factory** - 
- **Facade** - fornece uma interface simples e única para um conjunto de interfaces complexas de um subsistema, escondendo os detalhes internos de quem o usa.
- **Observer** — define uma relação de um-para-muitos entre objetos, onde quando um objeto muda de estado, todos os seus dependentes são notificados automaticamente.



