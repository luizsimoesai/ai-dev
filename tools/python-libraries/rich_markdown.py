# rich é usado para imprimir texto com cores, tabelas, barras de progresso e muito mais no terminal.

from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

console = Console()

# Texto colorido
console.print("[bold green]Sucesso![/bold green]")

# Criando uma tabela
table = Table(title="Usuários")
table.add_column("Nome", style="cyan")
table.add_column("Idade", justify="right")

table.add_row("Alice", "30")
table.add_row("Bob", "25")

console.print(table)


# ------------------
teste_markdown = """
# Markdown

- Item 1
- Item 2
- Item 3
"""

Markdown(teste_markdown)

