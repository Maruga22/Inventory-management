"""
Command-line client for the inventory management REST API.

Examples
--------
    python cli.py add --name "Coca-Cola 330ml" --barcode 5449000000996 --quantity 24 --price 0.99
    python cli.py list --category Beverages
    python cli.py view 1
    python cli.py update 1 --quantity 50
    python cli.py delete 1
    python cli.py lookup --barcode 5449000000996
    python cli.py import-product --barcode 5449000000996 --quantity 24 --price 0.99
"""
import json

import click
import requests

DEFAULT_API_URL = "http://127.0.0.1:5000/api"


def _print(data):
    click.echo(json.dumps(data, indent=2, default=str))


def _handle_response(resp):
    try:
        _print(resp.json())
    except ValueError:
        click.echo(f"Request failed with status {resp.status_code}: {resp.text}")


@click.group()
@click.option("--api-url", default=DEFAULT_API_URL, show_default=True,
              help="Base URL of the inventory API")
@click.pass_context
def cli(ctx, api_url):
    """Inventory Management CLI - talks to the Flask inventory REST API."""
    ctx.ensure_object(dict)
    ctx.obj["API_URL"] = api_url.rstrip("/")


@cli.command()
@click.option("--name", required=True, help="Product name")
@click.option("--barcode", default=None, help="Product barcode (EAN/UPC)")
@click.option("--category", default=None)
@click.option("--quantity", default=0, type=int, show_default=True)
@click.option("--price", default=0.0, type=float, show_default=True)
@click.option("--description", default=None)
@click.option("--brand", default=None)
@click.pass_context
def add(ctx, name, barcode, category, quantity, price, description, brand):
    """Add a new inventory item."""
    payload = {
        "name": name,
        "barcode": barcode,
        "category": category,
        "quantity": quantity,
        "price": price,
        "description": description,
        "brand": brand,
    }
    resp = requests.post(f"{ctx.obj['API_URL']}/inventory", json=payload)
    _handle_response(resp)


@cli.command("list")
@click.option("--name", default=None, help="Filter by name substring")
@click.option("--category", default=None, help="Filter by category substring")
@click.pass_context
def list_items(ctx, name, category):
    """List inventory items, optionally filtered."""
    params = {k: v for k, v in {"name": name, "category": category}.items() if v}
    resp = requests.get(f"{ctx.obj['API_URL']}/inventory", params=params)
    _handle_response(resp)


@cli.command()
@click.argument("item_id", type=int)
@click.pass_context
def view(ctx, item_id):
    """View a single inventory item by ID."""
    resp = requests.get(f"{ctx.obj['API_URL']}/inventory/{item_id}")
    _handle_response(resp)


@cli.command()
@click.argument("item_id", type=int)
@click.option("--name", default=None)
@click.option("--barcode", default=None)
@click.option("--category", default=None)
@click.option("--quantity", default=None, type=int)
@click.option("--price", default=None, type=float)
@click.option("--description", default=None)
@click.option("--brand", default=None)
@click.pass_context
def update(ctx, item_id, **fields):
    """Update one or more fields on an existing inventory item."""
    payload = {k: v for k, v in fields.items() if v is not None}
    if not payload:
        click.echo("Provide at least one field to update.")
        return
    resp = requests.put(f"{ctx.obj['API_URL']}/inventory/{item_id}", json=payload)
    _handle_response(resp)


@cli.command()
@click.argument("item_id", type=int)
@click.pass_context
def delete(ctx, item_id):
    """Delete an inventory item."""
    resp = requests.delete(f"{ctx.obj['API_URL']}/inventory/{item_id}")
    _handle_response(resp)


@cli.command()
@click.option("--barcode", default=None, help="Look up a product by barcode")
@click.option("--name", default=None, help="Search products by name")
@click.pass_context
def lookup(ctx, barcode, name):
    """Look up product details from OpenFoodFacts (does not save anything)."""
    if not barcode and not name:
        click.echo("Provide --barcode or --name")
        return
    params = {}
    if barcode:
        params["barcode"] = barcode
    if name:
        params["name"] = name
    resp = requests.get(f"{ctx.obj['API_URL']}/inventory/lookup", params=params)
    _handle_response(resp)


@cli.command("import-product")
@click.option("--barcode", required=True, help="Barcode of the product to import")
@click.option("--quantity", default=0, type=int, show_default=True)
@click.option("--price", default=0.0, type=float, show_default=True)
@click.pass_context
def import_product(ctx, barcode, quantity, price):
    """Fetch a product from OpenFoodFacts and save it directly as an inventory item."""
    payload = {"barcode": barcode, "quantity": quantity, "price": price}
    resp = requests.post(f"{ctx.obj['API_URL']}/inventory/import", json=payload)
    _handle_response(resp)


if __name__ == "__main__":
    cli(obj={})
