#!/usr/bin/env python
import datetime

import ovrlib.wi

voters = ovrlib.wi.lookup_voter(
    first_name="sage", last_name="weil", date_of_birth=datetime.datetime(1978, 3, 17)
)
print(voters)

election = ovrlib.wi.lookup_polling_place(voters[0].district_combo_id)
print(election)

ballot = ovrlib.wi.lookup_ballot_status(voters[0].voter_id, election.election_id)
print(ballot)
