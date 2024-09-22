import argparse
import textwrap

from f_fee_tui.app import FastFEEApp


def main():
    app = FastFEEApp()
    app.run()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="A Textual User Interface for monitoring and commanding the F-FEE.",
        epilog=textwrap.dedent(
            """
            Prerequisites:

            * The core services shall be running
            * The `feesim` shall be running unless you are testing real hardware
            * The `dpu_cs` shall be running
            * The `data_dump` shall be running when testing F-CAM

            Additional information:

            * TBW

        """),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    from f_fee_tui._version import get_version

    version = get_version()
    parser.add_argument('--version', action='version', version=f'f-fee-tui {version=}')

    args = parser.parse_args()

    main()
