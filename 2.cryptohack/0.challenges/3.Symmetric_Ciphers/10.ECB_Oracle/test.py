from rich.console import Console
from rich.table import Table

console = Console()

table = Table(title="Fruits")
table.add_column("Name", style="cyan")
table.add_column("Quantity", style="magenta")
table.add_row("Apple", "10")
table.add_row("Banana", "20")

console.print(table)

