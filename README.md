# DD-IX Enrollment Helpers

This little helper scripts creates user enrollment invites and sends them via email using listmonk.

## Prerequisites

- authentik: get a api token from a user with permissions to create user invites
- listmonk: get a api token for sending mails
- put the tokens in the `secret.ini` file (template: `secret.ini.ex`)

## create-invites.py

This script creates the invites in authentik:

- prepare a csv file (`username`, `full name`, `email`)
- `./create-invites.py < enroll.csv > invites.csv`

The script prints the csv file with an additional invite uuid. The output is to be parsed by the `send-invites.py` script.


## send-invites.py

*TBD*
