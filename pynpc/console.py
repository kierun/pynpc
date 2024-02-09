# -*- coding: utf-8 -*-
"""Main console cli entry point."""

import logging
import logging.config
import sys
from enum import Enum
from pathlib import Path
from typing import Annotated, Optional

import structlog
import typer
from mimesis.enums import Locale
from rich import print as rprint
from rich.console import Console
from rich.prompt import Confirm
from typer_config import use_yaml_config

from pynpc import __version__
from pynpc.npc import NPC
from pynpc.utils import COLOUR_INFO, VersionCheck, check_if_latest_version, join_with_oxford_commas, wprint

EXIT_CODE_SUCCESS = 0
EXIT_CODE_OPERATION_FAILED = 1
EXIT_CODE_SCRIPT_FAILED = 2
EXIT_CODE_SERVICE_ACCOUNT_FAILED = 3
EXIT_CODE_YAML_DATA_FAILED = 4


class LogLevels(str, Enum):
    """Log levels choices.

    https://typer.tiangolo.com/tutorial/parameter-types/enum/
    """

    critical = "critical"
    error = "error"
    warning = "warning"
    info = "info"
    debug = "debug"
    notset = "notset"


_outputs = ("console", "markdown", "latex")

app = typer.Typer()
pre_chain = [
    # Add the log level and a timestamp to the event_dict if the log entry
    # is not from structlog.
    structlog.stdlib.add_log_level,
    # Add extra attributes of LogRecord objects to the event dictionary
    # so that values passed in the extra parameter of log methods pass
    # through to log output.
    structlog.stdlib.ExtraAdder(),
]


def configure_logging(log_level: str, verbose: bool) -> None:
    """Configure all the logging."""
    # Logging levels
    # https://www.structlog.org/en/stable/_modules/structlog/_log_levels.html?highlight=log%20level
    _lvl = {
        "critical": 50,
        "error": 40,
        "warning": 30,
        "info": 20,
        "debug": 10,
        "notset": 0,
    }

    # Structlog processors. Order appears to matter…
    shared_processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.format_exc_info,
        structlog.processors.CallsiteParameterAdder(
            [
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            ],
        ),
    ]

    class VerboseFilter(logging.Filter):
        """Filter log entries on verbose flag."""

        def __init__(self, param: str = "") -> None:
            """Initialise."""
            self.param = param
            super()

        def filter(self, _: logging.LogRecord) -> bool:  # pyright: ignore [reportIncompatibleMethodOverride]
            # We have no choice in the method's name.
            # We do not care about record thus mark it as _.
            #
            # The pragam no cover can be removed once we actually use
            # something useful.
            return verbose  # pragma: no cover

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": True,  # tabula raza.
            "filters": {
                "myfilter": {
                    "()": VerboseFilter,  # -*- coding: utf-8 -*-
                    "param": "noshow",
                },
            },
            "formatters": {
                "plain": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        *shared_processors,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.processors.JSONRenderer(),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
                "colored": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        *shared_processors,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                        structlog.dev.ConsoleRenderer(colors=True),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
            },
            "handlers": {
                "default": {
                    "level": _lvl[log_level],
                    "class": "logging.StreamHandler",
                    "filters": ["myfilter"],
                    "formatter": "colored",
                },
                "file": {
                    "level": _lvl[log_level],
                    "class": "logging.handlers.WatchedFileHandler",
                    "filename": "pynpc.log",
                    "formatter": "plain",
                },
            },
            # Define all the loggers you want!
            "loggers": {
                "pynpc": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
                "requests": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
                "rich": {
                    "handlers": ["default", "file"],
                    "level": _lvl[log_level],
                    "propagate": True,
                },
            },
        },
    )
    structlog.configure(
        processors=[
            *shared_processors,  # type: ignore[list-item]
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(_lvl[log_level]),
        cache_logger_on_first_use=True,
    )


def callback_output(ctx: typer.Context, value: str) -> str | None:
    """Check output callback."""
    if ctx.resilient_parsing:
        return None  # pragma: no cover
    if value.lower() not in _outputs:
        err = f"Invalid output: '{value}', should be one of {join_with_oxford_commas(_outputs, conjunction='or')}"
        raise typer.BadParameter(err)
    return value


def callback_localisation(ctx: typer.Context, values: list[str]) -> list[str] | None:
    """Check localisation callback."""
    if ctx.resilient_parsing:
        return None  # pragma: no cover
    err = [x for x in values if x not in Locale.values()]
    if err:
        msg = f"Invalid localisation: '{join_with_oxford_commas(err)}' "
        msg += f"should be one of {join_with_oxford_commas(list(Locale.values()), conjunction='or')}"
        raise typer.BadParameter(msg)
    return values


# ruff: noqa: UP007
# ↑ Why? Because typer_config does not support UNION yet.
@app.command()
@use_yaml_config(default_value="config.yml")  # MUST BE AFTER @app.command()
def main(
    output: Annotated[str, typer.Argument(envvar="PYNPC_OUTPUT", callback=callback_output)] = "console",
    log_level: Annotated[
        LogLevels,
        typer.Option(case_sensitive=False, envvar="PYNPC_LOG_LEVEL"),
    ] = LogLevels.info,
    verbose: Annotated[bool, typer.Option(envvar="PYNPC_VERBOSE")] = False,
    version: Annotated[bool, typer.Option(envvar="PYNPC_VERSION")] = False,
    localisation: Annotated[
        Optional[list[str]],
        typer.Option("--localisation", "-l", envvar="PYNPC_LOCALS", callback=callback_localisation),
    ] = [  # noqa: B006
        "en",
        "ja",
        "fr",
    ],  # Do not use mutable data structures for argument defaults. But, in this case, this is fine.
) -> None:
    """Generate simple NPCs for table top role playing games."""
    # Prints the current version and exits.
    if version:
        rprint(__version__)
        sys.exit(EXIT_CODE_SUCCESS)

    # Configure logging.
    configure_logging(log_level.value, verbose)
    logger = structlog.get_logger("pynpc")
    logger.debug(
        "All the loggers",
        loggers=list(logging.root.manager.loggerDict),
    )
    logger.debug("locals", local=locals())

    # Configure the console.
    console = Console()
    console.rule(f"[{COLOUR_INFO}]TTRPG NPC generator via {output}")

    # Check latest version.
    _version_check()

    # Run commands.
    logger.debug("Starting real work…")
    _do_stuff(logger, output, localisation)

    # We should be done…
    logger.debug("That's all folks!")
    console.rule(f"[{COLOUR_INFO}]Operation was successful")
    sys.exit(EXIT_CODE_SUCCESS)


def _version_check() -> None:
    """Check if we are running the latest verion from GitHub."""
    check = check_if_latest_version()
    if check == VersionCheck.LATEST:
        wprint(f"This is the latest version {__version__}.", level="info")
    elif check == VersionCheck.LAGGING:
        wprint("there is a new version available: please update.", level="warning")
        if Confirm.ask("Exit and update?", default=True):
            wprint(
                "Please run [i]python -m pip install -U pynpc[/i]",
                level="info",
            )
            sys.exit(EXIT_CODE_SUCCESS)
        wprint("Proceeding with old version…", level="warning")
    elif check == VersionCheck.UNKNOWN:
        wprint("Could not check for newer versons.", level="warning")
    else:  # pragma: no cover
        # This should never, ever happen!
        wprint("This is bug, please report!", level="error")


def _do_stuff(logger: structlog.BoundLogger, output: str, localisation: list[str] | None) -> None:  # pragma: no cover
    """Do stuff.

    This has no unit tests since it does everything. We could mock
    everything, but why?
    """
    x = NPC(localisation=localisation)
    if output.lower() == "console":
        rprint(x)
    elif output.lower() == "markdown":  # pragma: no cover
        # This is super basic. It should be improved with tests.
        with Path("npc.md").open(mode="w") as f:
            f.write(x.to_markdown())
        logger.info(
            "pandoc command, if needed",
            cmd="pandoc --pdf-engine=xelatex -o npc.pdf npc.md",
        )
    elif output.lower() == "latex":  # pragma: no cover
        rprint("Not support yet")
    else:  # pragma: no cover
        rprint("Report a bug.")


if __name__ == "__main__":
    app()  # pragma: no cover
