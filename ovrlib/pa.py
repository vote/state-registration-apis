import base64
import datetime
import json
import logging
import re
from dataclasses import dataclass
from typing import Dict, Optional

import requests
from lxml import etree  # type: ignore

from .exceptions import (
    InvalidAccessKeyError,
    InvalidDLError,
    InvalidRegistrationError,
    InvalidSignatureError,
    ReadOnlyAccessKeyError,
)

STAGING_URL = "https://paovrwebapi.beta.votespa.com/SureOVRWebAPI/api/ovr"
PROD_URL = "https://paovrwebapi.votespa.com/SureOVRWebAPI/api/ovr"


logger = logging.getLogger("ovrlib.pa")


"""

These parts of the API are optional and not current supported:

- batch mode
- optional fields, like
  - race
  - ethnicity
  - need help to vote (+ preferred langauge)
  - is poll worker


"""

# A few regexes for normalize_address_unit()
RE_BARE_NUMBER = re.compile(r"^#?(\d+)$")
RE_BARE_UNIT_NUMBER = re.compile(r"^(\w+)\.? (\d+)$")
RE_TRAILING_NUMBER = re.compile(r"^(.*) #(\d+)$")
RE_TRAILING_UNIT_NUMBER = re.compile(r"^(.*) (\w+)\.? (\d+)$")


## API constants
#
# These constants are generated by querying the API.  You can generate updated code with
#
#   session = ovrlib.pa.Session(api_key=..., staging=True)
#   session.print_constants()

ERROR = {
    "VR_WAPI_InvalidAccessKey": "Access Key is Invalid.",
    "VR_WAPI_InvalidAction": "Action not found.",
    "VR_WAPI_InvalidAPIbatch": "Batch value is Invalid.",
    "VR_WAPI_InvalidOVRCounty": "Your county of residence is required.",
    "VR_WAPI_InvalidOVRDL": " please provide valid DL or pick continuesubmit checkbox.",
    "VR_WAPI_InvalidOVRDLformat": "Please enter a valid 8 digit PA driver's license or PennDOT ID card number.",
    "VR_WAPI_InvalidOVRDOB": "Please input a valid birth date.",
    "VR_WAPI_InvalidOVRemail": "The format of the email address is incorrect. Please correct and try again.",
    "VR_WAPI_InvalidOVRmailingzipcode": "The zip code must be 5 digits or 9 digits (zip code + 4).",
    "VR_WAPI_InvalidOVRphone": "The phone number provided is not valid. Please enter a valid phone number.",
    "VR_WAPI_InvalidOVRPreviousCounty": "Previous County of Registration is required for an Address Change application",
    "VR_WAPI_InvalidOVRPreviouszipcode": "Please enter a valid 5 digit zip code.",
    "VR_WAPI_InvalidOVRSSNformat": "Please enter the LAST FOUR digits of your Social Security number.",
    "VR_WAPI_InvalidOVRzipcode": "Please enter a valid 5 digit zip code.",
    "VR_WAPI_invalidpreviousregyear": "Please input valid year.",
    "VR_WAPI_InvalidReason": "Please select any one reason - New Application or Update Application , both are not allowed",
    "VR_WAPI_MissingAccessKey": "Please provide the access key in [sysparm_AuthKey] parameter in the link to proceed.",
    "VR_WAPI_MissingAddress": "A complete mailing or residential address is required for your application to be submitted online. Please use the link at the top of the page to print a blank voter registration application. Please complete, sign and date it then mail it to your county voter registration office. Do not FAX your application form.",
    "VR_WAPI_MissingAPIaction": "Please provide the GET action in [sysparm_action] parameter in the link to proceed.",
    "VR_WAPI_MissingCounty": "Please provide the county in [sysparm_County] parameter in the link to proceed.",
    "VR_WAPI_MissingLanguage": "Please provide the Language code in [sysparm_Language] parameter in the link to proceed.",
    "VR_WAPI_MissingOVRassistancedeclaration": "Please indicate assistance was provided with the completion of this form.",
    "VR_WAPI_MissingOVRcity": "Your city is required.",
    "VR_WAPI_MissingOVRcounty": "Your county of residence is required.",
    "VR_WAPI_MissingOVRdeclaration1": "Please confirm you have read and agree to the terms.",
    "VR_WAPI_MissingOVRDL": "Please supply either a PA driver's license or PennDOT ID card number, the last four digits of your SSN, or click the check box.",
    "VR_WAPI_MissingOVRfirstname": "Your first name is required.",
    "VR_WAPI_MissingOVRinterpreterlang": "Required if interpreter is checked",
    "VR_WAPI_MissingOVRisageover18": "Will you be 18 years or older on or before election day? You must provide a response before continuing. ",
    "VR_WAPI_MissingOVRisuscitizen": "Are you a citizen of the U.S.? You must provide a response before continuing.",
    "VR_WAPI_MissingOVRlastname": "Your last name is required.",
    "VR_WAPI_MissingOVROtherParty": "Warning - Party is not selected. If Other is selected, the Other party text box should be completed.",
    "VR_WAPI_MissingOVRPoliticalParty": "Warning - Party is not selected. If Other is selected, the Other party text box should be completed.",
    "VR_WAPI_MissingOVRPreviousAddress": "Address of Previous Registration is required for an Address Change application",
    "VR_WAPI_MissingOVRPreviousCity": "City of Previous Registration is required for an Address Change application",
    "VR_WAPI_MissingOVRPreviousFirstName": "Previous First Name is required for a Name Change application",
    "VR_WAPI_MissingOVRPreviousLastName": "Previous Last Name is required for a Name Change application",
    "VR_WAPI_MissingOVRPreviousZipCode": "Zip of Previous Registration is required for an Address Change application",
    "VR_WAPI_MissingOVRSSNDL": "Please supply either a PA driver's license or PennDOT ID card number, the last four digits of your SSN, or click the check box.",
    "VR_WAPI_MissingOVRstreetaddress": "Your street address is required.",
    "VR_WAPI_MissingOVRtypeofassistance": "Please select the type of assistance required.",
    "VR_WAPI_MissingOVRzipcode": "Your zip code is required",
    "VR_WAPI_MissingReason": "Please check at least one box.",
    "VR_WAPI_PennDOTServiceDown": "PennDOT server is down.",
    "VR_WAPI_RequestError": "WebAPi request is Invalid",
    "VR_WAPI_ServiceError": "Signature service is down.",
    "VR_WAPI_SystemError": "We're sorry, but the system cannot verify your information and complete your application right now. Try again.",
    "VR_WAPI_InvalidOVRAssistedpersonphone": "The phone number provided is not valid. Please enter a valid phone number.",
    "VR_WAPI_InvalidOVRsecondemail": "The format of the email address is incorrect. Please correct and try again.",
    "VR_WAPI_Invalidsignaturestring": "Your upload was not successful. Please try again.",
    "VR_WAPI_Invalidsignaturetype": "Please choose one of the following file types: .TIFF, .JPG, .BMP and .PNG.",
    "VR_WAPI_Invalidsignaturesize": "Please upload an image file size less than 5MB.",
    "VR_WAPI_Invalidsignaturedimension": "The image size should be equal to 180 x 60 pixels.",
    "VR_WAPI_Invalidsignaturecontrast": "Your upload was not successful. Please try again.",
    "VR_WAPI_MissingOVRParty": "Please select a political party.",
    "VR_WAPI_InvalidOVRPoliticalParty": "Please select a political party.",
    "VR_WAPI_Invalidsignatureresolution": "Your uploaded signature does not meet the 96.00 dpi requirements. Please upload an image file meeting or exceeding this requirement.",
    "VR_WAPI_MissingOVRmailinballotaddr": "Missing MailIn Ballot Address",
    "VR_WAPI_MissingOVRmailincity": "Missing MailIn City",
    "VR_WAPI_MissingOVRmailinstate": "Missing MailIn State",
    "VR_WAPI_InvalidOVRmailinzipcode": "Missing MailIn Zipcode",
    "VR_WAPI_MissingOVRmailinlivedsince": "Missing MailIn lived since",
    "VR_WAPI_MissingOVRmailindeclaration": "Missing MailIn Declaration",
    "VR_WAPI_MailinNotEligible": "MailIn Not Eligible",
    "VR_WAPI_InvalidIsTransferPermanent": "The transfer permanent flag provided is not valid",
}

UNIT_TYPE = {
    "apartment": "APT",
    "basement": "BSM",
    "box #": "BOX",
    "building": "BLD",
    "department": "DEP",
    "floor": "FL",
    "front": "FRN",
    "hanger": "HNG",
    "lobby": "LBB",
    "lot": "LOT",
    "lower": "LOW",
    "office": "OFC",
    "penthouse": "PH",
    "pier": "PIE",
    "poll": "POL",
    "rear": "REA",
    "room": "RM",
    "side": "SID",
    "slip": "SLI",
    "space": "SPC",
    "stop": "STO",
    "suite": "STE",
    "trailer": "TRLR",
    "unit": "UNI",
    "upper": "UPP",
    "cabin": "CBN",
    "hub": "HUB",
    "student mailing center": "SMC",
    "townhouse": "TH",
}

PARTY = {
    "democratic": "D",
    "republican": "R",
    "green": "GR",
    "libertarian": "LN",
    "none (no affiliation)": "NF",
    "other": "OTH",
}

GENDER = {"female": "F", "male": "M", "unknown": "U"}

XML_TEMPLATE = "<APIOnlineApplicationData xmlns='OVRexternaldata'>  <record>    <batch></batch>    <FirstName></FirstName>    <MiddleName></MiddleName>    <LastName></LastName>    <TitleSuffix></TitleSuffix>    <united-states-citizen></united-states-citizen>    <eighteen-on-election-day></eighteen-on-election-day>    <isnewregistration></isnewregistration>    <name-update></name-update>    <address-update></address-update>    <ispartychange></ispartychange>    <isfederalvoter></isfederalvoter>    <DateOfBirth></DateOfBirth>    <Gender></Gender>    <Ethnicity></Ethnicity>    <Phone></Phone>    <Email></Email>    <streetaddress></streetaddress>    <streetaddress2></streetaddress2>    <unittype></unittype>    <unitnumber></unitnumber>    <city></city>    <zipcode></zipcode>    <donthavePermtOrResAddress></donthavePermtOrResAddress>    <county></county>    <municipality></municipality>    <mailingaddress></mailingaddress>    <mailingcity></mailingcity>    <mailingstate></mailingstate>    <mailingzipcode></mailingzipcode>    <drivers-license></drivers-license>    <ssn4></ssn4>    <signatureimage></signatureimage>    <continueAppSubmit></continueAppSubmit>    <donthavebothDLandSSN></donthavebothDLandSSN>    <politicalparty></politicalparty>    <otherpoliticalparty></otherpoliticalparty>    <needhelptovote></needhelptovote>    <typeofassistance></typeofassistance>    <preferredlanguage></preferredlanguage>    <voterregnumber></voterregnumber>    <previousreglastname></previousreglastname>    <previousregfirstname></previousregfirstname>    <previousregmiddlename></previousregmiddlename>    <previousregaddress></previousregaddress>    <previousregcity></previousregcity>    <previousregstate></previousregstate>    <previousregzip></previousregzip>    <previousregcounty></previousregcounty>    <previousregyear></previousregyear>    <declaration1></declaration1>    <assistedpersonname></assistedpersonname>    <assistedpersonAddress></assistedpersonAddress>    <assistedpersonphone></assistedpersonphone>    <assistancedeclaration2></assistancedeclaration2>    <ispollworker></ispollworker>    <bilingualinterpreter></bilingualinterpreter>    <pollworkerspeaklang></pollworkerspeaklang>    <secondEmail></secondEmail>    <ismailin></ismailin>    <istransferpermanent></istransferpermanent>    <mailinaddresstype></mailinaddresstype>    <mailinballotaddr></mailinballotaddr>    <mailincity></mailincity>    <mailinstate></mailinstate>    <mailinzipcode></mailinzipcode>    <mailinward></mailinward>    <mailinlivedsince></mailinlivedsince>    <mailindeclaration></mailindeclaration>  </record></APIOnlineApplicationData>"

## end constants


@dataclass
class PAOVRElectionInfo:
    next_election: datetime.date
    next_vr_deadline: datetime.date
    vr_declaration: str
    vbm_election_name: str
    vbm_request_deadline: datetime.datetime
    vbm_request_declaration: str
    vbm_receipt_deadline: datetime.datetime


@dataclass
class PAOVRRequest:
    first_name: str
    last_name: str
    date_of_birth: datetime.date
    address1: str
    city: str
    county: str
    zipcode: str
    party: str
    united_states_citizen: bool
    eighteen_on_election_day: bool
    declaration: bool
    is_new: Optional[bool] = None

    signature: Optional[bytes] = None
    signature_type: Optional[str] = None

    middle_name: Optional[str] = None
    suffix: Optional[str] = None
    address2: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: Optional[str] = None  # "male", "female", "unknown", "M", "F", "U"
    federal_voter: Optional[bool] = None
    unit_type: Optional[str] = None
    unit_number: Optional[str] = None
    dl_number: Optional[str] = None
    ssn4: Optional[str] = None

    previous_first_name: Optional[str] = None
    previous_middle_name: Optional[str] = None
    previous_last_name: Optional[str] = None
    previous_address: Optional[str] = None
    previous_city: Optional[str] = None
    previous_state: Optional[str] = None
    previous_zipcode: Optional[str] = None
    previous_county: Optional[str] = None
    previous_year: Optional[str] = None

    mailing_address: Optional[str] = None
    mailing_city: Optional[str] = None
    mailing_state: Optional[str] = None
    mailing_zipcode: Optional[str] = None

    mailin_ballot_request: Optional[bool] = None
    mailin_ballot_to_registration_address: Optional[bool] = None
    mailin_ballot_to_mailing_address: Optional[bool] = None
    mailin_ballot_address: Optional[str] = None
    mailin_ballot_city: Optional[str] = None
    mailin_ballot_state: Optional[str] = None
    mailin_ballot_zipcode: Optional[str] = None

    def normalize_address_unit(self) -> None:
        """
        This takes a dict with one or more of [address1, address2,
        unittype, unitnumber] fields.  If the unit type/number are omitted, and
        a recognized unit is found in the address line(s), it will be moved into the
        dedicated unittype+unitnumber fields.
        """
        if self.unit_type or self.unit_number:
            return

        # first try address2 field
        if self.address2 is not None:
            m = RE_BARE_NUMBER.match(self.address2.strip())
            if m:
                self.unit_type = "UNIT"
                self.unit_number = m[1]
                self.address2 = None
                return

            m = RE_BARE_UNIT_NUMBER.match(self.address2.strip())
            if m:
                if m[1].lower() in UNIT_TYPE:
                    self.address2 = None
                    self.unit_type = UNIT_TYPE[m[1].lower()]
                    self.unit_number = m[2]
                    return
                if m[1].upper() in UNIT_TYPE.values():
                    self.address2 = None
                    self.unit_type = m[1].upper()
                    self.unit_number = m[2]
                    return

        # then look for suffix on address1
        # try trailing portion of address1
        m = RE_TRAILING_NUMBER.match(self.address1.strip())
        if m:
            self.address1 = m[1].strip()
            self.unit_type = "UNIT"
            self.unit_number = m[2]
            return

        m = RE_TRAILING_UNIT_NUMBER.match(self.address1.strip())
        if m:
            if m[2].lower() in UNIT_TYPE:
                self.address1 = m[1]
                self.unit_type = UNIT_TYPE[m[2].lower()]
                self.unit_number = m[3]
                return
            if m[2].upper() in UNIT_TYPE.values():
                self.address1 = m[1]
                self.unit_type = m[2].upper()
                self.unit_number = m[3]
                return

    def to_request_body(self) -> str:
        """
        Generate a valid registration request body
        """
        SIG_TYPES = ["tiff", "png", "jpg", "bmp", "jpeg"]

        REQUIRED = {
            "first_name": "FirstName",
            "last_name": "LastName",
            "date_of_birth": None,
            "address1": "streetaddress",
            "city": "city",
            "county": "county",
            "zipcode": "zipcode",
            "party": None,  # multiple
            "united_states_citizen": "united-states-citizen",
            "eighteen_on_election_day": "eighteen-on-election-day",
            "declaration": "declaration1",
        }

        OPTIONAL = {
            "is_new": None,
            "federal_voter": "isfederalvoter",
            "middle_name": "MiddleName",
            "suffix": "TitleSuffix",  # The API enumerates valid suffixes, but seems to accept any value here.
            "address2": "streetaddress2",
            "email": "email",
            "phone": "phone",
            "gender": None,
            # "race": None,
            "unit_type": None,
            "unit_number": None,
            "dl_number": "drivers-license",
            "ssn4": "ssn4",
            # if change of name, address
            "previous_first_name": "previousregfirstname",
            "previous_middle_name": "previousregmiddlename",
            "previous_last_name": "previousreglastname",
            "previous_address": "previousregaddress",
            "previous_city": "previousregcity",
            "previous_state": "previousregstate",
            "previous_zipcode": "previousregzip",
            "previous_county": "previousregcounty",
            "previous_year": "previousregyear",
            # mailing address
            "mailing_address": "Mailingaddress",
            "mailing_city": "mailingcity",
            "mailing_state": "mailingstate",
            "mailing_zipcode": "mailingzipcode",
            # VBM
            "mailin_ballot_request": "ismailin",
            "mailin_ballot_to_registration_address": None,
            "mailin_ballot_to_mailing_address": None,
            "mailin_ballot_address": "mailinballotaddr",
            "mailin_ballot_city": "mailincity",
            "mailin_ballot_state": "mailincity",
            "mailin_ballot_zipcode": "mailinzipcode",
        }

        self.normalize_address_unit()

        vals: Dict[str, str] = {
            "batch": "0",
        }
        for k in REQUIRED.keys():
            if not getattr(self, k):
                raise InvalidRegistrationError(f"registration field '{k}' is required")

        for k, f in list(REQUIRED.items()) + list(OPTIONAL.items()):
            v = getattr(self, k)
            if v is None:
                continue
            if k == "is_new":
                continue
            if k == "date_of_birth":
                vals["DateOfBirth"] = v.strftime("%Y-%m-%d")
            elif k == "party":
                party = v.lower()
                if party in ["democrat"]:
                    party = "democratic"
                elif not party or party.startswith("none"):
                    party = "none (no affiliation)"
                if party in PARTY:
                    vals["politicalparty"] = PARTY[party]
                else:
                    vals["politicalparty"] = PARTY["other"]
                    vals["otherpoliticalparty"] = party
            elif k == "gender":
                if v.lower() in GENDER:
                    vals["gender"] = GENDER[v].lower()
                elif v.upper() in GENDER.values():
                    vals["gender"] = v.upper()
                else:
                    raise InvalidRegistrationError(
                        f"gender '{v}' not recognized; must be one of {GENDER}"
                    )
            elif f:
                if v == True:
                    vals[f] = "1"
                elif v == False:
                    vals[f] = "0"
                else:
                    vals[f] = v
            else:
                raise RuntimeError(f"unhandled field {k}")

        if self.is_new == True:
            vals["isnewregistration"] = "1"
        elif self.previous_first_name:
            vals["name-update"] = "1"
        elif self.previous_address:
            vals["address-update"] = "1"
        elif self.is_new == False:
            vals["ispartychange"] = "1"
        else:
            # if we can't infer anything, assume that this is a new
            # registration.
            vals["isnewregistration"] = "1"

        if not self.dl_number:
            vals["continueAppSubmit"] = "1"
        if not self.dl_number and not self.ssn4:
            vals["donthavebothDLandSSN"] = "1"
            if not self.signature:
                raise InvalidRegistrationError(
                    "signature image required if DL and SSN are both missing"
                )

        if self.signature:
            if self.signature_type not in SIG_TYPES:
                raise InvalidRegistrationError(
                    f"signature_type must be one of {SIG_TYPES}"
                )
            sig_type = self.signature_type
            if sig_type == "jpeg":
                sig_type = "jpg"
            vals[
                "signatureimage"
            ] = f"data:image/{sig_type};base64,{base64.b64encode(self.signature).decode('utf-8')}"

        root = etree.fromstring(XML_TEMPLATE)
        for record in root:
            for i in record:
                k = i.tag.split("}")[1]  # strip of "{xmlns}" prefix
                if k in vals:
                    i.text = str(vals[k])
        xml = etree.tostring(root).decode("utf-8")
        return json.dumps({"ApplicationData": xml})


@dataclass
class PAOVRResponse:
    application_id: Optional[str]
    application_date: Optional[datetime.datetime]
    signature_source: Optional[str]

    @classmethod
    def from_response_body(cls, root):
        assert root.tag == "RESPONSE"
        application_id = None
        application_date = None
        signature = None
        for i in root:
            if i.tag == "APPLICATIONID":
                application_id = i.text
            elif i.tag == "APPLICATIONDATE":
                application_date = datetime.datetime.strptime(
                    i.text, "%b %d %Y %I:%M%p"
                )
            elif i.tag == "SIGNATURE":
                signature = i.text
        return cls(
            application_id=application_id,
            application_date=application_date,
            signature_source=signature,
        )


class PAOVRSession:
    def __init__(self, api_key: str, staging: bool, language: int = 0):
        self.api_key = api_key
        self.staging = staging
        self.language = language

    def get_url(self, action: str) -> str:
        if self.staging:
            url = STAGING_URL
        else:
            url = PROD_URL
        url += f"?JSONv2&sysparm_AuthKey={self.api_key}&sysparm_action={action}&sysparm_Language={self.language}"
        return url

    def do_request_unparsed(self, action: str, data=None) -> str:
        url = self.get_url(action)
        if data:
            response = requests.post(
                url,
                headers={
                    "Content-Type": "application/json",
                    "Cache-Control": "no-cache",
                },
                data=data,
            )
        else:
            response = requests.get(url)

        logger.debug(f"{action} Status: {response.status_code}")
        logger.debug(f"{action} Response: {response.text}")

        if response.status_code != 200:
            raise InvalidRegistrationError(f"HTTP status code {response.status_code}")

        return response.text

    def do_request(self, action: str, data=None) -> etree.Element:
        xml_str = json.loads(self.do_request_unparsed(action, data))
        root = etree.fromstring(xml_str)

        # check for errors only
        if root.tag == "RESPONSE":
            saw_application_id = None
            for i in root:
                if i.tag == "APPLICATIONID":
                    saw_application_id = True
                if i.tag != "ERROR":
                    continue
                if not i.text:
                    continue
                if i.text == "VR_WAPI_InvalidAccessKey":
                    raise InvalidAccessKeyError(f"{i.text}: {ERROR.get(i.text)}")
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
                    raise InvalidSignatureError(f"{i.text}: {ERROR.get(i.text, '')}")
                else:
                    raise InvalidRegistrationError(f"{i.text}: {ERROR.get(i.text, '')}")
            if not saw_application_id:
                # This seems to happen when we submit a registration that is missing some XML fields:
                # no error, and no valid response.
                raise InvalidRegistrationError(
                    "empty response (incomplete registration request?)"
                )

        return root

    def get_election_info(self) -> PAOVRElectionInfo:
        other_map = {
            "NextElection": ("NextElection", "next_election"),
            "NextVRDeadline": ("NextVRDeadline", "next_vr_deadline"),
            "Text_OVRApplnDeclaration": ("Text", "vr_declaration"),
            "Text_OVRMailInApplnDeclaration": ("Text", "vbm_request_declaration"),
            "Text_OVRMailInApplnComplDate": (
                "Text_OVRMailInApplnComplDate",
                "vbm_request_date",
            ),
            "Text_OVRMailInBallotRecvdDate": (
                "Text_OVRMailInBallotRecvdDate",
                "vbm_receipt_date",
            ),
            "Text_OVRMailInElectionName": ("ElectionName", "vbm_election_name"),
            "Text_OVRMailInApplnComplTime": ("Time", "vbm_request_time"),
            "Text_OVRMailInBallotRecvdTime": ("RecvdTime", "vbm_receipt_time"),
        }

        r = {}
        root = self.do_request("GETAPPLICATIONSETUP")
        assert root.tag == "NewDataSet"
        for i in root:
            if i.tag in other_map:
                for j in i:
                    if j.tag == other_map[i.tag][0]:
                        r[other_map[i.tag][1]] = j.text

        return PAOVRElectionInfo(
            next_election=r["next_election"],
            next_vr_deadline=r["next_vr_deadline"],
            vr_declaration=r["vr_declaration"],
            vbm_election_name=r["vbm_election_name"],
            vbm_request_deadline=datetime.datetime.strptime(
                f"{r['vbm_request_date']} {r['vbm_request_time']}", "%m/%d/%Y %I:%M %p"
            ),
            vbm_receipt_deadline=datetime.datetime.strptime(
                f"{r['vbm_receipt_date']} {r['vbm_receipt_time']}", "%m/%d/%Y %I:%M %p"
            ),
            vbm_request_declaration=r["vbm_request_declaration"],
        )

    def print_constants(self) -> None:
        """
        Print code to update API constants
        """
        r = self.fetch_constants()
        print("ERROR = %s\n" % json.dumps(r["error"], indent=4))
        print("UNIT_TYPE = %s\n" % json.dumps(r["unit_type"], indent=4))
        print("PARTY = %s\n" % json.dumps(r["party"], indent=4))
        print("GENDER = %s\n" % json.dumps(r["gender"], indent=4))
        print("XML_TEMPLATE = %s\n" % json.dumps(r["xml_template"]))

    def fetch_constants(self) -> Dict[str, Dict[str, str]]:
        """
        Make read-only queries to the PA OVR API to fetch various
        constants, XML template
        """
        rval: Dict[str, Dict[str, str]] = {
            "error": {},
            "county": {},
            "suffix": {},
            "state": {},
            "party": {},
            "gender": {},
            "race": {},
            "unit_type": {},
            "assistance_type": {},
        }

        def map_subitem(node, keytag: str, valtag: str, target: Dict[str, str]):
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
        for i in root:
            if i.tag == "MessageText":
                map_subitem(i, "ErrorCode", "ErrorText", rval["error"])

        root = self.do_request("GETAPPLICATIONSETUP")
        assert root.tag == "NewDataSet"

        def map_subitem_lower(node, keytag: str, valtag: str, target: Dict[str, str]):
            k = None
            v = None
            for j in node:
                if j.tag == keytag:
                    k = j.text
                elif j.tag == valtag:
                    v = j.text
            if k is not None and v is not None:
                target[k.lower()] = v

        for i in root:
            if i.tag == "Suffix":
                map_subitem_lower(
                    i, "NameSuffixDescription", "NameSuffixCode", rval["race"]
                )
            elif i.tag == "Race":
                map_subitem_lower(i, "RaceDescription", "RaceCode", rval["race"])
            elif i.tag == "UnitTypes":
                map_subitem_lower(
                    i, "UnitTypesDescription", "UnitTypesCode", rval["unit_type"]
                )
            elif i.tag == "AssistanceType":
                map_subitem(
                    i,
                    "AssistanceTypeDescription",
                    "AssistanceTypeCode",
                    rval["assistance_type"],
                )
            elif i.tag == "Gender":
                map_subitem_lower(i, "GenderDescription", "GenderCode", rval["gender"])
            elif i.tag == "PoliticalParty":
                map_subitem_lower(
                    i, "PoliticalPartyDescription", "PoliticalPartyCode", rval["party"]
                )
            elif i.tag == "County":
                map_subitem_lower(i, "Countyname", "countyID", rval["county"])
            elif i.tag == "States":
                map_subitem_lower(i, "CodesDescription", "Code", rval["state"])
            else:
                pass

        rval["xml_template"] = json.loads(self.do_request_unparsed("GETXMLTEMPLATE"))

        return rval

    def register(self, registration: PAOVRRequest) -> PAOVRResponse:
        """
        Submit a voter registration
        """
        body = registration.to_request_body()
        try:
            root = self.do_request("SETAPPLICATION", data=body)
        except InvalidAccessKeyError:
            # see if we can do a read-only request
            self.do_request("GETERRORVALUES")
            # we can; API key is read-only
            raise ReadOnlyAccessKeyError(
                f"Your API key is read-only; check with your contact at the PA Secretary of State's office to make it read-write"
            )
        except Exception as e:
            raise e
        return PAOVRResponse.from_response_body(root)
