#!/usr/bin/env python3
"""
CLI para gerenciar o Price Monitor.

Uso:
  python cli.py add <url> [--price 299.99]
  python cli.py list
  python cli.py remove <id>
  python cli.py check
  python cli.py run
"""
import click
from rich.console import Console
from rich.table import Table
from rich import box

from app.db.database import init_db, get_session
from app.db.models import Product, PriceHistory
from app.scrapers import get_scraper
from app.notifications.email_sender import send_price_alert
from app.notifications.telegram_bot import send_telegram_alert

console = Console()


@click.group()
def cli():
    """🔍 Price Monitor — rastreie preços de produtos online."""
    init_db()


@cli.command()
@click.argument("url")
@click.option("--price", "-p", default=None, type=float, help="Preço alvo para alertas")
def add(url, price):
    """Adiciona um produto para monitoramento."""
    with console.status(f"[cyan]Buscando produto em {url}..."):
        try:
            scraper = get_scraper(url)
        except ValueError:
            console.print(f"[red]✗ Nenhum scraper disponível para essa URL.[/red]")
            raise SystemExit(1)

        result = scraper.scrape(url)

    with get_session() as session:
        if session.query(Product).filter(Product.url == url).first():
            console.print("[yellow]⚠ Produto já está sendo monitorado.[/yellow]")
            return

        product = Product(
            name=result.name, url=url,
            store=result.store, target_price=price,
        )
        session.add(product)
        session.flush()

        if result.price:
            session.add(PriceHistory(
                product_id=product.id, price=result.price, available=result.available,
            ))
        session.commit()

    console.print(f"[green]✓ Adicionado:[/green] {result.name}")
    if result.price:
        console.print(f"  Preço atual: [bold]R$ {result.price:,.2f}[/bold]")
    if price:
        console.print(f"  Meta de alerta: R$ {price:,.2f}")


@cli.command("list")
def list_products():
    """Lista todos os produtos monitorados."""
    with get_session() as session:
        products = session.query(Product).filter(Product.active == True).all()

    if not products:
        console.print("[dim]Nenhum produto monitorado ainda.[/dim]")
        return

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("ID",    style="dim",    width=4)
    table.add_column("Loja",  style="yellow", width=14)
    table.add_column("Nome",                  width=40)
    table.add_column("Preço",                 width=12, justify="right")
    table.add_column("Meta",                  width=12, justify="right")

    for p in products:
        price_str = f"R$ {p.latest_price:,.2f}" if p.latest_price else "—"
        target_str = f"R$ {p.target_price:,.2f}" if p.target_price else "—"
        table.add_row(str(p.id), p.store, p.name[:40], price_str, target_str)

    console.print(table)


@cli.command()
@click.argument("product_id", type=int)
def remove(product_id):
    """Remove um produto do monitoramento."""
    with get_session() as session:
        product = session.get(Product, product_id)
        if not product:
            console.print(f"[red]✗ Produto #{product_id} não encontrado.[/red]")
            return
        name = product.name
        session.delete(product)
        session.commit()
    console.print(f"[green]✓ Removido:[/green] {name}")


@cli.command()
def check():
    """Verifica preços de todos os produtos agora (uma vez)."""
    from app.scheduler import check_all_products
    check_all_products()


@cli.command()
def run():
    """Inicia o scheduler contínuo."""
    from app.scheduler import run_scheduler
    run_scheduler()


if __name__ == "__main__":
    cli()
