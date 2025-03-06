import click
import asyncio
from consultant_info_generator.service.consultant_import import import_consultants


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--profile-ids", "-p", type=str, help="Profile IDs to import", required=True
)
@click.option(
    "--remove-existing", "-r", is_flag=True, help="Remove existing consultants"
)
def import_consultants_command(profile_ids: str, remove_existing: bool):
    imported = asyncio.run(import_consultants(profile_ids.split(","), remove_existing))
    click.echo(f"Imported {len(imported)} consultants")


if __name__ == "__main__":
    """
    This is the entry point for the CLI.
    Usage: python consultant_info_generator\cli\main.py
    """
    cli()
