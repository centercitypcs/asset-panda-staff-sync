# vim:ft=just:

# set constants
DATA_DIR := env_var("DATA_DIR") # copied from environment
SQL_DIR := justfile_directory() / "sql"
SCRIPTS_DIR := justfile_directory() / "scripts"
INPUT_DIR := DATA_DIR / "in"
OUTPUT_DIR := DATA_DIR / "out"
PS_STAFF_FILE := INPUT_DIR / "ps_staff.csv"
AP_STAFF_FILE := INPUT_DIR / "Staff_csv_list.csv"
AP_UPDATE_FILE := OUTPUT_DIR / "asset_panda_staff_updates.csv"

# query parameters
FIRST_DAY := "first_day=31-AUG-2024"

# list all recipes
_default: ensure_data_dir
    @just --list --unsorted

# ensure DATA_DIRs exist
[private]
ensure_data_dir:
    #!/usr/bin/env bash
    umask 0077
    mkdir -p {{INPUT_DIR}}
    mkdir -p {{OUTPUT_DIR}}

# attach to the PowerSchool VPN
[private]
attach_vpn:
    #!/usr/bin/env bash

    set -euo pipefail
    OPEN_CONNECT="$(which openconnect)"

    # exit if already attached
    PIDFILE="/var/run/openconnect.pid"
    if [[ -f "${PIDFILE}" ]]; then
        echo "VPN already attached!"
        exit
    fi

    echo "Attaching VPN"
    echo "${F5_PASSWORD}" | sudo "${OPEN_CONNECT}" \
        --background \
        --passwd-on-stdin \
        --pid-file="${PIDFILE}" \
        --protocol=f5 \
        --quiet \
        --user="${F5_USERNAME}" \
        --servercert="${F5_SERVERCERT}" \
        "${F5_CONNECT_URL}" >/dev/null

# detach from the PowerSchool VPN
[private]
detach_vpn:
    #!/usr/bin/env bash
    set -euo pipefail

    # exit if already detached
    PIDFILE="/var/run/openconnect.pid"
    if [[ ! -f "${PIDFILE}" ]]; then
        echo "No VPN attached!"
        exit
    fi

    echo "Detaching VPN"
    sudo kill -s TERM $(cat "${PIDFILE}")

# export staff data from PowerSchool to CSV
@export_ps_staff: ensure_data_dir attach_vpn && detach_vpn
    echo "exporting PowerSchool staff to {{PS_STAFF_FILE}} ... \c"
    records {{SQL_DIR}}/select_staff.sql csv | sed -e 's/\r$//' -e '/^$/d' >{{PS_STAFF_FILE}}
    echo finished!

# generate a CSV of staff updates to import into AssetPanda
@gen-asset-panda-staff-updates: ensure_data_dir export_ps_staff
    echo "writing staff updates to {{AP_UPDATE_FILE}} ... \c"
    python {{SCRIPTS_DIR}}/export_staff_records.py {{PS_STAFF_FILE}} {{AP_STAFF_FILE}} {{AP_UPDATE_FILE}}
    echo finished!
