import datetime
from dataclasses import dataclass
from typing import Optional

import requests

SEARCH_ENDPOINT = (
    "https://myvote.wi.gov/DesktopModules/GabMyVoteModules/api/voter/search"
)
POLLING_PLACE_ENDPOINT = "https://myvote.wi.gov/DesktopModules/GabMyVoteModules/api/address/pollingplace/{district_combo_id}"
BALLOT_ENDPOINT = "https://myvote.wi.gov/DesktopModules/GabMyVoteModules/api/absentee/progressbarinfo/{voter_id}?electionid={election_id}"


@dataclass
class WIAbsenteeBallotStatus:
    request_submitted: Optional[datetime.datetime]
    request_approved: Optional[datetime.datetime]
    created: Optional[datetime.datetime]
    sent: Optional[datetime.datetime]
    expected_delivery: Optional[datetime.datetime]
    received: Optional[datetime.datetime]
    returned: Optional[datetime.datetime]

    ballot_rejected: Optional[bool]
    request_denied: Optional[bool]
    ballot_received_issue: Optional[str]
    foreign_address: Optional[bool]

    @classmethod
    def from_api_response(cls, info):
        def from_date(s):
            if s:
                return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(
                    tzinfo=datetime.timezone.utc
                )
            return None

        return cls(
            request_submitted=from_date(info.get("absenteeRequestSubmittedDate")),
            request_approved=from_date(info.get("absenteeRequestApprovedDate")),
            created=from_date(info.get("absenteeBallotCreatedDate")),
            sent=from_date(info.get("absenteeBallotSentDate")),
            expected_delivery=from_date(
                info.get("absenteeBallotAnticipatedDeliveryDate")
            ),
            received=from_date(info.get("completedAbsenteeBallotReceivedDate")),
            returned=from_date(info.get("dateBallotReturned")),
            ballot_rejected=info.get("isDateBallotReturnedRejected"),
            request_denied=info.get("isAbsenteeRequestDenied"),
            ballot_received_issue=info.get("hasAbsenteeBallotReceivedIssue"),
            foreign_address=info.get("isForeignAddress"),
        )


@dataclass
class WIElection:
    election_id: str
    start: datetime.datetime
    end: datetime.datetime
    description: str

    polling_place_ward: str

    polling_place_id: str
    polling_place_description: str
    polling_place_address: str
    polling_place_city: str
    polling_place_state: str
    polling_place_zipcode: str
    polling_place_lat: float
    polling_place_lng: float


@dataclass
class WIVoterRegistration:
    full_name: str
    address: str
    city: str
    state: str
    zipcode: str

    date_of_birth: datetime.date

    status: str
    status_reason: str

    registration_date: datetime.date
    registration_source: str

    voter_reg_number: str  # NOTE: should this be an integer?

    voter_id: str
    district_combo_id: str
    jurisdiction_id: str

    @property
    def active(self):
        return self.status == "Active"

    @property
    def last_name(self):
        return self.full_name.split(",")[0]

    @property
    def first_and_middle_name(self):
        self.full_name.split(",")[1]

    @classmethod
    def from_api_response(cls, info):
        dob = info.get("dateOfBirth")
        if dob and not dob.startswith("01/01/1900"):
            dob = datetime.datetime.strptime(dob[0:10], "%Y-%m-%d").date()
        else:
            dob = None
        r = cls(
            full_name=info.get("voterName"),
            date_of_birth=dob,
            address=info.get("address"),
            city=info.get("city"),
            state=info.get("state"),
            zipcode=info.get("postalCode"),
            status=info.get("voterStatusName"),
            status_reason=info.get("statusReasonName"),
            registration_date=datetime.datetime.strptime(
                info.get("registrationDate"), "%m/%d/%Y"
            ).date(),
            registration_source=info.get("registrationSource"),
            voter_reg_number=info.get("voterRegNumber"),
            voter_id=info.get("voterID"),
            district_combo_id=info.get("districtComboID"),
            jurisdiction_id=info.get("jurisdictionID"),
        )
        return r


def lookup_voter(first_name, last_name, date_of_birth, **kwargs):
    response = requests.post(
        SEARCH_ENDPOINT,
        headers={"content-type": "application/x-www-form-urlencoded",},
        data={
            "firstName": first_name,
            "lastName": last_name,
            "birthDate": date_of_birth.strftime("%m/%d/%Y"),
        },
        **kwargs
    )
    if not response.json().get("Success"):
        return None
    r = []
    for info in response.json()["Data"]["voters"]["$values"]:
        r.append(WIVoterRegistration.from_api_response(info))
    return r


def lookup_polling_place(district_combo_id, **kwargs):
    response = requests.get(
        POLLING_PLACE_ENDPOINT.format(district_combo_id=district_combo_id),
        headers={"content-type": "application/x-www-form-urlencoded",},
        **kwargs
    )
    if not response.json().get("Success"):
        return None
    info = response.json()["Data"]

    # note the "date" is midnight local time in UTC.  we'll adjust the hour/minute and create
    # datetimes with no timezone.
    date = datetime.datetime.strptime(
        info.get("electionDate"), "%Y-%m-%dT%H:%M:%SZ"
    ).replace(tzinfo=datetime.timezone.utc)
    print(date)
    start_time = datetime.datetime.strptime(info.get("startTime"), "%I.%M %p")
    end_time = datetime.datetime.strptime(info.get("endTime"), "%I.%M %p")
    start = date + datetime.timedelta(hours=start_time.hour, minutes=start_time.hour)
    end = date + datetime.timedelta(hours=end_time.hour, minutes=end_time.minute)
    return WIElection(
        election_id=info.get("electionID"),
        start=start,
        end=end,
        description=info.get("electionDescription"),
        polling_place_ward=info.get("wardName"),
        polling_place_id=info.get("pplid"),
        polling_place_description=info.get("pollingLocationName"),
        polling_place_address=info.get("ppL_Address"),
        polling_place_city=info.get("ppL_City"),
        polling_place_state="WI",
        polling_place_zipcode=info.get("ppL_PostalCode"),
        polling_place_lat=float(info.get("latitude")),
        polling_place_lng=float(info.get("longitude")),
    )


def lookup_ballot_status(voter_id, election_id, **kwargs):
    response = requests.get(
        BALLOT_ENDPOINT.format(voter_id=voter_id, election_id=election_id),
        headers={"content-type": "application/x-www-form-urlencoded",},
        **kwargs
    )
    if not response.json().get("Success"):
        return None
    return WIAbsenteeBallotStatus.from_api_response(response.json()["Data"])
