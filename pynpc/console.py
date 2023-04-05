# -*- coding: utf-8 -*-
"""Console entry point."""
from __future__ import annotations

import logging
import logging.config
import sys

import click
import structlog
from click_help_colors import HelpColorsCommand  # type: ignore[import]
from rich.console import Console
from rich.prompt import Confirm
from rich.traceback import install

from pynpc import __version__
from pynpc.utils import (
    COLOUR_INFO,
    VersionCheck,
    check_if_latest_version,
    wprint,
)

# Rich.
install(show_locals=True)

EXIT_CODE_SUCCESS = 0
EXIT_CODE_OPERATION_FAILED = 1
EXIT_CODE_SCRIPT_FAILED = 2
EXIT_CODE_SERVICE_ACCOUNT_FAILED = 3
EXIT_CODE_YAML_DATA_FAILED = 4


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
    # https://www.structlog.org/en/stable/_modules/structlog/_log_levels.html?highlight=log%20level  # noqa: E501
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
            ]
        ),
    ]

    class VerboseFilter(logging.Filter):
        """Filter log entries on verbose flag."""

        def __init__(self, param: str = "") -> None:
            """Initialise."""
            self.param = param
            super()

        def filter(self, _: logging.LogRecord) -> bool:  # noqa: A003
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
                    "()": VerboseFilter,
                    "param": "noshow",
                }
            },
            "formatters": {
                "plain": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        *shared_processors,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,  # noqa: E501
                        structlog.processors.JSONRenderer(),
                    ],
                    "foreign_pre_chain": pre_chain,
                },
                "colored": {
                    "()": structlog.stdlib.ProcessorFormatter,
                    "processors": [
                        *shared_processors,
                        structlog.stdlib.ProcessorFormatter.remove_processors_meta,  # noqa: E501
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
        }
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


@click.command(
    cls=HelpColorsCommand,
    help_headers_color="blue",
    help_options_color="magenta",
)
@click.option(
    "-l",
    "--log-level",
    default="info",
    show_default=True,
    type=click.Choice(
        ["notset", "debug", "info", "warning", "error", "critical"],
        case_sensitive=False,
    ),
    help="Chose the logging level from the available options. "
    "This affect the file logs as well.",
)
@click.option(
    "-v", "--version", is_flag=True, help="Print the version and exit"
)
@click.option("--verbose", is_flag=True, help="Print the logs to stdout")
def main(
    log_level: str,
    version: bool,
    verbose: bool,
) -> None:
    """Generate simple NPCs for table top role playing games."""
    # Prints the current version and exits.
    if version:
        click.echo(__version__)
        sys.exit(EXIT_CODE_SUCCESS)

    # Configure logging.
    configure_logging(log_level, verbose)
    logger = structlog.get_logger("pynpc")
    logger.debug(
        "All the loggers",
        loggers=list(logging.root.manager.loggerDict),
    )

    # Configure the console.
    console = Console()
    console.rule(f"[{COLOUR_INFO}]TTRPG NPC generator")

    # Check latest version.
    _version_check()

    # Run commands.
    logger.debug("Starting real work…")

    # We should be done…
    logger.debug("That's all folks!")
    wprint("Operation was successful.", level="success")
    sys.exit(EXIT_CODE_SUCCESS)


def _version_check() -> None:
    """Check if we are running the latest verion from GitHub."""
    check = check_if_latest_version()
    if check == VersionCheck.LATEST:
        wprint(f"This is the latest version {__version__}.", level="info")
    elif check == VersionCheck.LAGGING:
        wprint(
            "there is a new version available: please update.", level="warning"
        )
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


if __name__ == "__main__":  # pragma: no cover
    main()
