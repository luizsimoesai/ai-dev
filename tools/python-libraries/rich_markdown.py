# rich is used to print colored text, tables, progress bars, and much more in the terminal.

from rich.console import Console
from rich.table import Table
from rich.markdown import Markdown

console = Console()

# Colored text
console.print("[bold green]Success![/bold green]")

# Creating a table
table = Table(title="Users")
table.add_column("Name", style="cyan")
table.add_column("Age", justify="right")

table.add_row("Alice", "30")
table.add_row("Bob", "25")

console.print(table)


# ------------------
test_markdown = """
# Markdown

- Item 1
- Item 2
- Item 3
"""

Markdown(test_markdown)

