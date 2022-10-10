""" 
Module to define CLI using Typer
"""

import logging
import re
import sys

import typer
from natsort import natsorted
from rich import print

from snapper import utils

from pydavinci import davinci

utils.setup_rich_logging()
from pyfiglet import Figlet

logger = logging.getLogger(__name__)
logger.setLevel("INFO")

fig = Figlet(font="rectangles")

app = typer.Typer()
print(fig.renderText("snapper"))
print("[bold]Create and manage DaVinci Resolve timeline revisions :fish:\n")


@app.command()
def new(
    dry_run: bool = typer.Option(
        False, help="Don't duplicate the timeline, just return the next version name"
    )
):
    """Create a new timeline snapshot"""

    resolve = davinci.Resolve()

    print(f"[cyan]Getting current timeline :bulb:")
    current_timeline = resolve.active_timeline
    current_timeline_name = current_timeline.name

    def get_next_version_name():
        """Get the next version number for current timeline"""

        versions = []
        for timeline in resolve.project.timelines:

            if timeline is not None:

                logger.debug(f'[magenta]Found timeline: "{timeline.name}"')
                if re.search(
                    rf"^({current_timeline_name})(\s)(V\d+)",
                    timeline.name,
                    re.IGNORECASE,
                ):
                    logger.debug(f"[magenta]Found snapshot: {timeline.name}")
                    versions.append(timeline.name)

        # If none exist, start first
        if len(versions) == 0:

            logger.debug(f"[magenta]No snapshots exist. Starting first.")
            return f"{current_timeline_name} V1"

        # Get last snapshot version
        last_version = natsorted(versions).pop()
        logger.debug(f"[magenta]Last snapshot version: {last_version}")

        # Increment snapshot version number
        next_version = re.sub(
            r"[0-9]+$",
            lambda x: f"{str(int(x.group())+1).zfill(len(x.group()))}",
            last_version,
        )

        next_version = str(next_version)
        logger.debug(f"[magenta]Next snapshot version: '{next_version}'")
        return next_version

    print(f"[cyan]Getting next snapshot version :mag_right:")
    next_version_name = get_next_version_name()

    if dry_run:

        print(
            "[bold][yellow]Dry-run enabled:[/bold] No timeline snapshot will be created."
        )
        utils.app_exit(0)

    print(f"[yellow]Cloning timeline :dna:")
    current_timeline.name = next_version_name  # Rename original
    current_timeline.duplicate_timeline(current_timeline_name)
    print(
        f"[green]Latest snapshot: [bold]'{next_version_name}'[/bold] :heavy_check_mark:"
    )
    utils.app_exit(0, 2)


def tidy_into_snapshots_folder():
    """Tidy loose timeline snapshots into a versions folder"""
    # TODO: Implement version tidy up script


@app.callback()
def main(
    verbose: bool = typer.Option(False, help="Log debug messages"),
):
    """
    Do yourself a favour and create frequent timeline snapshots.
    Don't leave messy little experiments at the end of your timelines.
    Keep it tidy. Keep it clean.

    Just type: "snapper new"
    """

    if verbose:
        logger.setLevel("DEBUG")


if __name__ == "__main__":
    app()
