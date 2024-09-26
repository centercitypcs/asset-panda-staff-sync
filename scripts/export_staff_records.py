#!/usr/bin/env python
"""
Export Staff Records from PowerSchool to Asset Panda Import File
"""

from pathlib import Path

import click
import pandas as pd


@click.command()
@click.argument("ps_staff_file", type=click.Path(exists=True, readable=True))
@click.argument("ap_staff_file", type=click.Path(exists=True, readable=True))
@click.argument(
    "output_file", type=click.Path(writable=True, allow_dash=True, path_type=Path)
)
def cli(ps_staff_file: Path, ap_staff_file: Path, output_file: Path) -> None:
    """Process command line arguments for StaffUpdater

    Args:
        ps_staff_file: path to CSV file of current PowerSchool staff
        ap_staff_file: path to CSV file of current Asset Panda staff
        output_file: path for CSV output of updates to apply to Asset Panda via
            import (may use "-" to send to stdout)

    Returns:
        None
    """
    staff_updater = StaffUpdater(ps_staff_file, ap_staff_file, output_file)
    staff_updater.write_updates()


class StaffUpdater:
    FIELDS: list[str] = [
        "Email",
        "Last Name",
        "First Name",
        "Job Title",
        "Location",
        "Status",
    ]

    def __init__(
        self, ps_staff_file: Path, ap_staff_file: Path, output_file: Path
    ) -> None:
        """Generate a CSV file with staff updates to apply to AssetPanda

        Compare staff data dumps from both PowerSchool and Asset Panda to output a
        file of updates to be applied to the staff records in Asset Panda.

        Args:
            ps_staff_file: path to CSV file of current PowerSchool staff
            ap_staff_file: path to CSV file of current Asset Panda staff
            output_file: path for CSV output of updates to apply to Asset Panda via
                import (may use "-" to send to stdout)

        Returns:
            None
        """

        self.ps_staff = StaffUpdater.process_ps_staff_file(ps_staff_file)
        self.ap_staff = StaffUpdater.process_ap_staff_file(ap_staff_file)
        self.output_file = output_file

    @classmethod
    def process_ps_staff_file(cls, ps_staff_file: Path) -> pd.DataFrame:
        """Process PowerSchool Staff File

        Import staff data from PowerSchool export file and filter out any staff
        entries that don't have a @centercitypcs.org email addresses.

        Args:
            cls: StaffUpdater class
            ps_staff_file: path to CSV file of current PowerSchool staff

        Returns:
            pandas.DataFrame of filtered results
        """
        return (
            pd.read_csv(ps_staff_file, dtype="str")
            .query("Email.notna()")
            .query("Email.str.endswith('@centercitypcs.org')")
            .set_index("Employee ID")
        )

    @classmethod
    def process_ap_staff_file(cls, ap_staff_file: Path) -> pd.DataFrame:
        """Process PowerSchool Staff File

        Import staff data from Asset Panda export file and filter out any staff
        that are not marked as Active.

        Args:
            cls: StaffUpdater class
            ap_staff_file: path to CSV file of current PowerSchool staff

        Returns:
            pandas.DataFrame of filtered results
        """
        return (
            pd.read_csv(ap_staff_file, dtype="str")
            .query("Status=='Active'")
            .set_index("Employee ID")
        )

    @property
    def updated_staff(self) -> pd.DataFrame:
        """Generate list of staff updates

        Compare demographic and location information for staff from PowerSchool
        and Asset Panda data and list of those who need their information
        updated in Asset Panda.

        Args:
            self: StaffUpdater instance

        Returns:
            pandas.DataFrame of staff needing updates
        """
        return (
            self.ps_staff.join(self.ap_staff, how="inner", rsuffix="_AP")
            .query(
                "Email != Email_AP |"
                "`Last Name` != `Last Name_AP` |"
                "`First Name` != `First Name_AP` |"
                "`Job Title` != `Job Title_AP` |"
                "`Location` != `Location_AP`"
            )
            .filter(items=StaffUpdater.FIELDS)
        )

    @property
    def new_staff(self) -> pd.DataFrame:
        """Generate list of new staff

        Generate list of staff found in PowerSchool who don't exist, or aren't
        active, in Asset Panda.

        Args:
            self: StaffUpdater instance

        Returns:
            pandas.DataFrame of new staff
        """
        return (
            self.ps_staff.join(self.ap_staff, how="left", rsuffix="_AP")
            .query("Email_AP.isna()")
            .filter(items=StaffUpdater.FIELDS)
        )

    @property
    def departed_staff(self) -> pd.DataFrame:
        """Generate list of departed staff

        Generate list of staff found in Asset Panda who are no longer active in
        PowerSchool.

        Args:
            self: StaffUpdater instance

        Returns:
            pandas.DataFrame of departed staff
        """
        return (
            self.ap_staff.join(self.ps_staff, how="left", rsuffix="_PS")
            .query("Email_PS.isna()")
            .assign(Status="Inactive")
            .filter(items=StaffUpdater.FIELDS)
        )

    def write_updates(self) -> None:
        """Write CSV file of Asset Panda updates

        Export a list of new, updated, and departed staff to a CSV file
        appropriate for importing into the Asset Panda staff list.

        Args:
            self: StaffUpdater instance

        Returns:
            None
        """
        if self.output_file.name == "-":
            self.output_file = Path("/dev/stdout")

        pd.concat([self.updated_staff, self.new_staff, self.departed_staff]).to_csv(
            self.output_file
        )


if __name__ == "__main__":
    # run the CLI if invoked as a script
    cli()
