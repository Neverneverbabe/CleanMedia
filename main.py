"""Entry point for CleanMedia.
Detects whether to run GUI or command-line interface."""

import sys

from gui.launcher_gui import main as launch_gui


def cli_main():
    """Placeholder for CLI interface."""
    print("CLI mode not yet implemented.")


def main():
    if '--gui' in sys.argv:
        launch_gui()
    else:
        cli_main()


if __name__ == '__main__':
    main()
