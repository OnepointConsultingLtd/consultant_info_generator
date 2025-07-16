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
    read_consultants,
)
from consultant_info_generator.service.question_order import order_questions_and_save
from consultant_info_generator.service.footanstey.webpage_import import (
    import_footanstey_consultants,
    FOOTANSTEY_URL,
)
from consultant_info_generator.logger import logger
from consultant_info_generator.service.category_extraction import (
    flatten_dimensions,
    extract_dimensions,
)
from consultant_info_generator.service.consultant_chat_preparation import (
    prepare_category_questions_and_assignments,
)
from consultant_info_generator.model.questions import CategoryQuestions
from consultant_info_generator.model.category_assignments import (
    ProfileCategoryAssignments,
)


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
    await _asave_questions_and_categories(
        category_questions, profile_category_assignments, remove_existing
    )


async def _asave_questions_and_categories(
    category_questions: CategoryQuestions,
    profile_category_assignments: ProfileCategoryAssignments,
    remove_existing: bool,
):
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


@cli.command()
@click.option(
    "--remove-existing", "-r", is_flag=True, help="Remove existing consultants"
)
@click.option(
    "--scrape", "-r", is_flag=True, help="scrape"
)
def import_footanstey(remove_existing: bool, scrape: bool):
    asyncio.run(_aimport_footanstey(remove_existing, scrape))


async def _aimport_footanstey(remove_existing: bool, scrape: bool):
    if scrape:
        consultants = await import_footanstey_consultants(FOOTANSTEY_URL)
    else:
        consultants = await read_consultants()
    categories = flatten_dimensions(
        await extract_dimensions(
            [consultant.model_dump_json() for consultant in consultants]
        )
    )
    category_questions, profile_category_assignments = (
        await prepare_category_questions_and_assignments(categories, consultants)
    )
    await _asave_questions_and_categories(
        category_questions, profile_category_assignments, remove_existing
    )


if __name__ == "__main__":
    """
    This is the entry point for the CLI.
    Usage: python consultant_info_generator/cli/main.py
    """
    cli()
