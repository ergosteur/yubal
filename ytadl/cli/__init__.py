"""YTADL CLI - command registration and entry point."""

from ytadl.cli.app import app
from ytadl.cli.doctor import doctor
from ytadl.cli.download import download
from ytadl.cli.import_cmd import import_music
from ytadl.cli.info import info
from ytadl.cli.nuke import nuke
from ytadl.cli.serve import serve
from ytadl.cli.sync import sync
from ytadl.cli.tag import tag
from ytadl.cli.version import version

# Explicit command registration
app.command()(doctor)
app.command()(download)
app.command(name="import")(import_music)
app.command()(info)
app.command()(nuke)
app.command()(serve)
app.command()(sync)
app.command()(tag)
app.command()(version)


def main() -> None:
    """Entry point for the CLI."""
    app()
