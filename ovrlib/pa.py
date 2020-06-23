import base64
import copy
import json
import logging
import re

import requests
from lxml import etree

STAGING_URL = "https://paovrwebapi.beta.votespa.com/SureOVRWebAPI/api/ovr"
PROD_URL = "https://paovrwebapi.votespa.com/SureOVRWebAPI/api/ovr"


logger = logging.getLogger("pa_ovr")


"""

These parts of the API are optional and not current supported:

- batch mode
- optional fields, like
  - gender
  - race
  - ethnicity
  - phone
  - email
  - need help to vote (+ preferred langauge)
  - is poll worker
- vote-by-mail registration / mail-in ballot request


"""


class InvalidAccessKeyError(Exception):
    pass


class ReadOnlyAccessKeyError(Exception):
    pass


class InvalidRegistrationError(Exception):
    pass


class InvalidDLError(Exception):
    pass


class InvalidSignatureError(Exception):
    pass


class Session:
    def __init__(self, api_key, staging, language=0):
        self.api_key = api_key
        self.staging = staging
        self.language = language
        self.setup()

    def get_url(self, action):
        if self.staging:
            url = STAGING_URL
        else:
            url = PROD_URL
        url += f"?JSONv2&sysparm_AuthKey={self.api_key}&sysparm_action={action}&sysparm_Language={self.language}"
        return url

    def do_request(self, action, data=None):
        url = self.get_url(action)
        if data:
            response = requests.post(url, data=data)
        else:
            response = requests.get(url)

        logger.debug(f"{action} {response.status_code}")
        # logger.debug(response.text)

        xml_str = json.loads(response.text)
        root = etree.fromstring(xml_str)

        # check for errors only
        if root.tag == "RESPONSE":
            for i in root:
                if i.tag != "ERROR":
                    continue
                if i.text == "VR_WAPI_InvalidAccessKey":
                    raise InvalidAccessKeyError(f"{i.text}: {self.error.get(i.text)}")
                elif i.text == "VR_WAPI_InvalidOVRDL":
                    raise InvalidDLError
                elif i.text in [
                    "VR_WAPI_Invalidsignaturestring",
                    "VR_WAPI_Invalidsignaturetype",
                    "VR_WAPI_Invalidsignaturesize",
                    "VR_WAPI_Invalidsignaturedimension",
                    "VR_WAPI_Invalidsignaturecontrast",
                    "VR_WAPI_Invalidsignatureresolution",
                ]:
                    raise InvalidSignatureError(f"{i.text}: {self.error.get(i.text)}")
                else:
                    raise InvalidRegistrationError(
                        f"{i.text}: {self.error.get(i.text)}"
                    )

        return root

    def setup(self):
        """
        Make initial read-only queries to the PA OVR API to gather constants and templates.
        """

        def map_subitem(node, keytag, valtag, target):
            k = None
            v = None
            for j in node:
                if j.tag == keytag:
                    k = j.text
                elif j.tag == valtag:
                    v = j.text
            if k is not None and v is not None:
                target[k] = v

        root = self.do_request("GETERRORVALUES")
        self.error = {}
        for i in root:
            if i.tag == "MessageText":
                map_subitem(i, "ErrorCode", "ErrorText", self.error)

        root = self.do_request("GETAPPLICATIONSETUP")
        assert root.tag == "NewDataSet"

        self.suffix = {}
        self.state = {}
        self.county = {}
        self.party = {}
        self.gender = {}
        self.race = {}
        self.unit_type = {}
        self.unit_type_reverse = {}
        self.assistance_type = {}
        self.other = {}

        def map_subitem_lower(node, keytag, valtag, target):
            k = None
            v = None
            for j in node:
                if j.tag == keytag:
                    k = j.text
                elif j.tag == valtag:
                    v = j.text
            if k is not None and v is not None:
                target[k.lower()] = v.lower()

        other_map = {
            "NextElection": ("NextElection", "next_election"),
            "NextVRDeadline": ("NextVRDeadline", "next_ovr_deadline"),
            "Text_OVRMailInApplnDeclaration": ("Text", "vbm_request_declaration"),
            "Text_OVRMailInApplnComplDate": (
                "Text_OVRMailInApplnComplDate",
                "vbm_postmark_date",
            ),
            "Text_OVRMailInBallotRecvdDate": (
                "Text_OVRMailInBallotRecvdDate",
                "vfm_receive_date",
            ),
            "Text_OVRMailInElectionName": ("ElectionName", "vbm_election_name"),
            "Text_OVRMailInApplnComplTime": ("Time", "vbm_postmark_time"),
            "Text_OVRMailInBallotRecvdTime": ("RecvdTime", "vbm_receive_time"),
        }

        for i in root:
            if i.tag == "Suffix":
                map_subitem_lower(
                    i, "NameSuffixDescription", "NameSuffixCode", self.race
                )
            elif i.tag == "Race":
                map_subitem_lower(i, "RaceDescription", "RaceCode", self.race)
            elif i.tag == "UnitTypes":
                map_subitem_lower(
                    i, "UnitTypesDescription", "UnitTypesCode", self.unit_type
                )
                map_subitem_lower(
                    i, "UnitTypesCode", "UnitTypesDescription", self.unit_type_reverse
                )
            elif i.tag == "AssistanceType":
                map_subitem_lower(
                    i,
                    "AssistanceTypeDescription",
                    "AssistanceTypeCode",
                    self.assistance_type,
                )
            elif i.tag == "Gender":
                map_subitem_lower(i, "GenderDescription", "GenderCode", self.gender)
            elif i.tag == "PoliticalParty":
                map_subitem_lower(
                    i, "PoliticalPartyDescription", "PoliticalPartyCode", self.party
                )
            elif i.tag in other_map:
                for j in i:
                    if j.tag == other_map[i.tag][0]:
                        self.other[other_map[i.tag][1]] = j.text
            elif i.tag == "County":
                map_subitem_lower(i, "Countyname", "countyID", self.county)
            elif i.tag == "States":
                map_subitem_lower(i, "CodesDescription", "Code", self.state)
            else:
                pass

        self.xml_template = self.do_request("GETXMLTEMPLATE")

    def register(self, registration, signature=None, signature_type=None, is_new=True):
        """
        Submit a voter registratio
        """

        SIG_TYPES = ["tiff", "png", "jpg", "bmp"]

        REQUIRED = {
            "first_name": "FirstName",
            "last_name": "LastName",
            "date_of_birth": None,
            "address1": "streetaddress",
            "city": "city",
            "county": None,
            "zipcode": "zipcode",
            "party": None,  # multiple
        }

        OPTIONAL = {
            "middle_name": "MiddleName",
            "suffix": None,
            "address2": "streetaddress2",
            # "email": "email",
            # "gender": None,
            # "race": None,
            # "phone": "phone",
            "unittype": None,
            "unitnumber": None,
            "dl_number": "drivers-license",
            "ssn4": "ssn4",
            "previous_first_name": "previousregfirstname",
            "previous_middle_name": "previousregmiddlename",
            "previous_last_name": "previousreglastname",
            "previous_address": "previousregaddress",
            "previous_city": "previousregcity",
            "previous_state": "previousregstate",
            "previous_zipcode": "previousregzip",
            "previous_county": "previousregcounty",
            "previous_year": "previousregyear",
        }

        for k in registration.keys():
            if k not in REQUIRED and k not in OPTIONAL:
                raise InvalidRegistrationError(f"registration field {k} not recognized")

        vals = {
            "batch": "0",
            "united-states-citizen": "1",
            "eighteen-on-election-day": "1",
            "declaration1": "1",
        }
        for k, v in REQUIRED.items():
            if k not in registration:
                raise InvalidRegistrationError(f"registration field {k} is required")
            if k == "date_of_birth":
                vals["DateOfBirth"] = registration[k].strftime("%Y-%m-%d")
            elif k == "address1":
                # attempt to extract out unit/apt numbers
                address = registration[k]
                p = re.compile(r"^(.+) #(\d+)$")
                m = p.match(address)
                if m:
                    address = m[1]
                    vals["unittype"] = "UNIT"
                    vals["unitnumber"] = m[2]
                else:
                    p = re.compile(r"^(.+) ([\w]+)\.? (\d+)$")
                    m = p.match(address)
                    if m:
                        if m[2].lower() in self.unit_type:
                            vals["unittype"] = self.unit_type[m[2].lower()].upper()
                            vals["unitnumber"] = m[3]
                        elif m[2].lower in self.unit_type_reverse:
                            vals["unittype"] = m[2].upper()
                            vals["unitnumber"] = m[3]
                vals["address"] = address

            elif k == "county":
                county = registration[k].lower()
                if county not in self.county:
                    raise InvalidRegistrationError(
                        f"county {county} is not recognized by the API"
                    )
                vals["county"] = self.county[county]
            elif k == "party":
                party = registration[k].lower()
                if party in ["democrat"]:
                    party = "democratic"
                elif party.startswith("none"):
                    party = "none (no affiliation)"
                if party in self.party:
                    vals["politicalparty"] = self.party[party]
                else:
                    vals["politicalparty"] = self.party["other"]
                    vals["otherpoliticalparty"] = party
            elif v:
                vals[v] = registration[k]
            else:
                raise RuntimeError(f"unhandled field {k}")

        for k, v in OPTIONAL.items():
            if k not in registration:
                continue
            if k == "suffix":
                # NOTE: the API enumerates specific suffixes; not sure what happens if we
                # submit one that is not listed.
                vals["TitleSuffix"] = registration[k].upper()
            elif v:
                vals[v] = registration[k]
            else:
                raise RuntimeError(f"unhandled field {k}")

        if is_new:
            vals["isnewregistration"] = "1"
        elif "previous_first_name" in registration:
            vals["name-update"] = "1"
        elif "previous_address" in registration:
            vals["address-update"] = "1"
        else:
            vals["ispartychange"] = "1"

        # FIXME: isfederalvoter

        if "dl_nubmer" not in registration:
            vals["continueAppSubmit"] = "1"
        if "dl_number" not in registration and "ssn4" not in registration:
            vals["donthavebothDLandSSN"] = "1"
            if not signature:
                raise InvalidRegistrationError(
                    "signature image required if DL and SSN are both missing"
                )

        if signature:
            if signature_type not in SIG_TYPES:
                raise InvalidRegistrationError(
                    f"signature_type must be one of {SIG_TYPES}"
                )
            vals[
                "signatureimage"
            ] = f"data:image/{signature_type};base64,{base64.b64encode(signature)}"

        root = copy.deepcopy(self.xml_template)
        for record in root:
            for i in record:
                k = i.tag.split("}")[1]
                if k in vals:
                    i.text = vals[k]

        xml = etree.tostring(root).decode("utf-8")
        logger.debug(f"Submission: {json.dumps(xml)}")

        root = self.do_request("SETAPPLICATION")
        assert root.tag == "RESPONSE"
        application_id = None
        application_date = None
        for i in root:
            if i.tag == "APPLICATIONID":
                application_id = i.text
            elif i.tag == "APPLICATIONDATE":
                application_id = i.text

        return {
            "application_id": application_id,
            "application_date": application_date,
        }