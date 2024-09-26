# Asset Panda Staff Sync

## Introduction

This project provides a scripts and queries to compare staff lists between
PowerSchool and Asset Panda and then produce a CSV update file to load into
AssetPanda to bring it into compliance with PowerSchool.

## Requirements

This project will run on macOS or Linux. It may run in Windows Subsystem for
Linux, try it and let me know!

### Required Packages

The following packages must be installed on the host:

- [direnv](https://direnv.net/) - execution environment management
- [uv](https://docs.astral.sh/uv/) - python interpreter and dependency
management
- [just](https://just.systems/man/en/introduction.html) - a command runner for
project-specific commands
- [openconnect](https://www.infradead.org/openconnect/) - cross-platform
multi-protocol SSL VPN client

Up-to-date versions of these packages are available via
[homebrew](https://brew.sh/) on macOS and Linux.

### Requirement Enviroment Variables

The following variables must be supplied from the execution enviroment:

- DATABASE_URL - a SQLAlchemy compatible [database URL](https://docs.sqlalchemy.org/en/20/core/engines.html#database-urls) for the
                 PowerSchool database.
- F5_USERNAME - PowerSchool VPN username
- F5_PASSWORD - PowerSchool VPN password
- F5_CONNECT_URL - PowerSchool VPN connect URL
- DATA_DIR - directory path on the local host to read and write data from/to

These are secrets and should be pulled on depend from secure storage. This
installation assumes you have them set in the `.env` file which is NOT STORED
in source control.

## Operation

### Step 1

Request a CSV staff report from Asset Panda. You should receive an email with a
link to download a CSV file. Download this file to the `INPUT_DIR` defined in
the `Justfile`.

### Step 2

Run `just` at the command prompt in the project directory to see options:

```console
$ just Available recipes:
     export_ps_staff               # export staff data from PowerSchool to CSV
     gen-asset-panda-staff-updates # generate a CSV of staff updates to import
                                   # into AssetPanda
```

then run:

```console
just gen-asset-panda-staff-updates
```

The `gen-asset-panda-staff-updates` recipe will create CSV file in the
OUTPUT_DIR named `asset_panda_staff_updates.csv` which can be imported into the
Asset Panda STAFF resources to bring the values there into sync with
PowerSchool data.
