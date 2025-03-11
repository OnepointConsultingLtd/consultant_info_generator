import click
import asyncio
from pathlib import Path

from consultant_info_generator.service.consultant_import import import_consultants
from consultant_info_generator.service.consultant_chat_preparation import (
    prepare_consultant_chat,
)
from consultant_info_generator.service.persistence_service_consultants_async import (
    save_category_question,
    save_profile_category_assignment,
    delete_category_question,
    delete_profile_category_assignment,
)
from consultant_info_generator.service.question_order import order_questions_and_save
from consultant_info_generator.logger import logger


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


@cli.command()
@click.option(
    "--profile-ids", "-p", type=str, help="Profile IDs to import", required=True
)
@click.option(
    "--remove-existing", "-r", is_flag=True, help="Remove existing consultants"
)
def import_consultants_with_categories(profile_ids: str, remove_existing: bool):
    asyncio.run(aimport_consultants_with_categories(profile_ids, remove_existing))


@cli.command()
@click.option(
    "--file", "-f", type=str, help="File with profile IDs to import", required=True
)
@click.option(
    "--remove-existing", "-r", is_flag=True, help="Remove existing consultants"
)
def import_consultants_with_categories_file(file: str, remove_existing: bool):
    profile_file = Path(file)
    if not profile_file.exists():
        click.echo(f"File {file} does not exist")
        return
    profile_ids = ",".join(profile_file.read_text(encoding="utf-8").splitlines())
    asyncio.run(aimport_consultants_with_categories(profile_ids, remove_existing))


async def aimport_consultants_with_categories(profile_ids: str, remove_existing: bool):
    profile_ids = profile_ids.split(",")
    logger.info(
        f"Importing consultants with categories for {len(profile_ids)} profiles"
    )
    imported = await import_consultants(profile_ids, remove_existing)
    logger.info(f"Imported {len(imported)} consultants")
    category_questions, profile_category_assignments = await prepare_consultant_chat(
        profile_ids
    )

    for category_question in category_questions.category_questions:
        if remove_existing:
            await delete_category_question(category_question)
        await save_category_question(category_question)
    for (
        profile_category_assignment
    ) in profile_category_assignments.profile_category_assignments:
        if remove_existing:
            await delete_profile_category_assignment(profile_category_assignment)
        await save_profile_category_assignment(profile_category_assignment)

    await order_questions_and_save()


if __name__ == "__main__":
    """
    This is the entry point for the CLI.
    Usage: python consultant_info_generator\cli\main.py
    """
    cli()
