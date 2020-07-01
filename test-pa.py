#!/usr/bin/env python
import argparse
import datetime
import json
import logging
import sys

import ovrlib.pa

logging.basicConfig(level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument("api_key", help="API key provided from PA")
parser.add_argument(
    "--with-dl", help="pass a PennDOT DL", action="store_true", required=False
)
parser.add_argument(
    "--with-ssn", help="pass last 4 of SSN", action="store_true", required=False
)
parser.add_argument("--signature", help="signature file", required=False)
parser.add_argument(
    "--election-info",
    help="fetch upcoming election info",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--get-constants",
    help="print all constants fetched from API",
    action="store_true",
    required=False,
)
parser.add_argument(
    "--print-constants-code",
    help="print API constants (e.g., to update code)",
    action="store_true",
    required=False,
)
args = parser.parse_args()

session = ovrlib.pa.PAOVRSession(api_key=args.api_key, staging=True)

if args.get_constants:
    r = session.fetch_constants()
    print(json.dumps(r, indent=4))
    sys.exit()

if args.print_constants_code:
    session.print_constants()
    sys.exit()

if args.election_info:
    print(session.get_election_info())
    sys.exit()

# test registration
sig = None
sig_type = None
if args.signature:
    with open(args.signature, "rb") as f:
        sig = f.read()
        sig_type = args.signature.split(".")[-1]

req = ovrlib.pa.PAOVRRequest(
    first_name="Sally",
    last_name="Penndot",
    suffix="XIV",
    date_of_birth=datetime.date(year=1944, month=5, day=2),
    address1="123 A St",
    city="Clarion",
    zipcode="16214",
    county="Clarion",
    gender="female",
    party="Democrat",
    federal_voter=True,
    united_states_citizen=True,
    eighteen_on_election_day=True,
    declaration=True,
)
if args.with_dl:
    req.dl_number = "99007069"
if args.with_ssn:
    req.ssn4 = "1234"

print(req.to_request_body())
response = session.register(req)
print(response)
