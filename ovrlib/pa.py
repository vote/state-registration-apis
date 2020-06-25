import base64
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
  - race
  - ethnicity
  - need help to vote (+ preferred langauge)
  - is poll worker


"""

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

GENDER = {
    "female": "F",
    "male": "M",
    "unknown": "U"
}

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

XML_TEMPLATE = "<APIOnlineApplicationData xmlns='OVRexternaldata'>  <record>    <batch></batch>    <FirstName></FirstName>    <MiddleName></MiddleName>    <LastName></LastName>    <TitleSuffix></TitleSuffix>    <united-states-citizen></united-states-citizen>    <eighteen-on-election-day></eighteen-on-election-day>    <isnewregistration></isnewregistration>    <name-update></name-update>    <address-update></address-update>    <ispartychange></ispartychange>    <isfederalvoter></isfederalvoter>    <DateOfBirth></DateOfBirth>    <Gender></Gender>    <Ethnicity></Ethnicity>    <Phone></Phone>    <Email></Email>    <streetaddress></streetaddress>    <streetaddress2></streetaddress2>    <unittype></unittype>    <unitnumber></unitnumber>    <city></city>    <zipcode></zipcode>    <donthavePermtOrResAddress></donthavePermtOrResAddress>    <county></county>    <municipality></municipality>    <mailingaddress></mailingaddress>    <mailingcity></mailingcity>    <mailingstate></mailingstate>    <mailingzipcode></mailingzipcode>    <drivers-license></drivers-license>    <ssn4></ssn4>    <signatureimage></signatureimage>    <continueAppSubmit></continueAppSubmit>    <donthavebothDLandSSN></donthavebothDLandSSN>    <politicalparty></politicalparty>    <otherpoliticalparty></otherpoliticalparty>    <needhelptovote></needhelptovote>    <typeofassistance></typeofassistance>    <preferredlanguage></preferredlanguage>    <voterregnumber></voterregnumber>    <previousreglastname></previousreglastname>    <previousregfirstname></previousregfirstname>    <previousregmiddlename></previousregmiddlename>    <previousregaddress></previousregaddress>    <previousregcity></previousregcity>    <previousregstate></previousregstate>    <previousregzip></previousregzip>    <previousregcounty></previousregcounty>    <previousregyear></previousregyear>    <declaration1></declaration1>    <assistedpersonname></assistedpersonname>    <assistedpersonAddress></assistedpersonAddress>    <assistedpersonphone></assistedpersonphone>    <assistancedeclaration2></assistancedeclaration2>    <ispollworker></ispollworker>    <bilingualinterpreter></bilingualinterpreter>    <pollworkerspeaklang></pollworkerspeaklang>    <secondEmail></secondEmail>    <ismailin></ismailin>    <istransferpermanent></istransferpermanent>    <mailinaddresstype></mailinaddresstype>    <mailinballotaddr></mailinballotaddr>    <mailincity></mailincity>    <mailinstate></mailinstate>    <mailinzipcode></mailinzipcode>    <mailinward></mailinward>    <mailinlivedsince></mailinlivedsince>    <mailindeclaration></mailindeclaration>  </record></APIOnlineApplicationData>"


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

        logger.debug(f"{action} {response.status_code}")

        if response.status_code != 200:
            raise InvalidRegistrationError(f"HTTP status code {response.status_code}")

        xml_str = json.loads(response.text)
        root = etree.fromstring(xml_str)

        # check for errors only
        if root.tag == "RESPONSE":
            for i in root:
                if i.tag != "ERROR":
                    continue
                if not i.text:
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
                    raise InvalidSignatureError(f"{i.text}: {ERROR.get(i.text, '')}")
                else:
                    raise InvalidRegistrationError(
                        f"{i.text}: {ERROR.get(i.text, '')}"
                    )

        return root

    def fetch_constants(self):
        """
        Make read-only queries to the PA OVR API to produce the constants
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
        error = {}
        for i in root:
            if i.tag == "MessageText":
                map_subitem(i, "ErrorCode", "ErrorText", error)
        print("ERRORS = %s\n" % json.dumps(error, indent=4))

        root = self.do_request("GETAPPLICATIONSETUP")
        assert root.tag == "NewDataSet"

        county = {}
        suffix = {}
        state = {}
        party = {}
        gender = {}
        race = {}
        unit_type = {}
        assistance_type = {}

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
                target[k.lower()] = v

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
                    i, "NameSuffixDescription", "NameSuffixCode", race
                )
            elif i.tag == "Race":
                map_subitem_lower(i, "RaceDescription", "RaceCode", race)
            elif i.tag == "UnitTypes":
                map_subitem_lower(
                    i, "UnitTypesDescription", "UnitTypesCode", unit_type
                )
            elif i.tag == "AssistanceType":
                map_subitem_lower(
                    i,
                    "AssistanceTypeDescription",
                    "AssistanceTypeCode",
                    assistance_type,
                )
            elif i.tag == "Gender":
                map_subitem_lower(i, "GenderDescription", "GenderCode", gender)
            elif i.tag == "PoliticalParty":
                map_subitem_lower(
                    i, "PoliticalPartyDescription", "PoliticalPartyCode", party
                )
            elif i.tag in other_map:
                for j in i:
                    if j.tag == other_map[i.tag][0]:
                        self.other[other_map[i.tag][1]] = j.text
            elif i.tag == "County":
                map_subitem_lower(i, "Countyname", "countyID", county)
            elif i.tag == "States":
                map_subitem_lower(i, "CodesDescription", "Code", state)
            else:
                pass

        print("UNIT_TYPE = %s\n" % json.dumps(unit_type, indent=4))
        print("PARTY = %s\n" % json.dumps(party, indent=4))
        print("GENDER = %s\n" % json.dumps(gender, indent=4))

    def normalize_address_unit(self, addr):
        """
        This takes a dict with one or more of [address1, address2,
        unittype, unitnumber] fields.  If the unit type/number are omitted, and
        a recognized unit is found in the address line(s), it will be moved into the
        dedicated unittype+unitnumber fields.
        """
        if addr.get("unittype") is not None or addr.get("unitnumber") is not None:
            return

        # first try address2 field
        if "address2" in addr:
            m = re.compile(r"^#?(\d+)$").match(addr["address2"].strip())
            if m:
                addr["unittype"] = "UNIT"
                addr["unitnumber"] = m[1]
                del addr["address2"]
                return

            m = re.compile(r"^(\w+)\.? (\d+)$").match(addr["address2"].strip())
            if m:
                if m[1].lower() in UNIT_TYPE:
                    del addr["address2"]
                    addr["unittype"] = self.unit_type[m[1].lower()]
                    addr["unitnumber"] = m[2]
                    return
                if m[1].upper() in UNIT_TYPE.values():
                    del addr["address2"]
                    addr["unittype"] = m[1].upper()
                    addr["unitnumber"] = m[2]
                    return

        # then look for suffix on address1
        if "address1" in addr:
            # try trailing portion of address1
            p1 = re.compile(r"^(.*) #(\d+)$")
            p2 = re.compile(r"^(.*) (\w+)\.? (\d+)$")

            m = p1.match(addr["address1"].strip())
            if m:
                addr["address1"] = m[1].strip()
                addr["unittype"] = "UNIT"
                addr["unitnumber"] = m[2]
                return

            m = p2.match(addr["address1"].strip())
            if m:
                if m[2].lower() in self.unit_type:
                    addr["address1"] = m[1]
                    addr["unittype"] = self.unit_type[m[2].lower()]
                    addr["unitnumber"] = m[3]
                    return
                if m[2].upper() in self.unit_type.values():
                    addr["address1"] = m[1]
                    addr["unittype"] = m[2].upper()
                    addr["unitnumber"] = m[3]
                    return

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
            "county": "county",
            "zipcode": "zipcode",
            "party": None,  # multiple
        }

        OPTIONAL = {
            "federal_voter": None,
            "middle_name": "MiddleName",
            "suffix": None,
            "address2": "streetaddress2",
            "email": "email",
            "phone": "phone",
            "gender": None,
            # "race": None,
            "unittype": None,
            "unitnumber": None,
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

        for k in registration.keys():
            if k not in REQUIRED and k not in OPTIONAL:
                raise InvalidRegistrationError(f"registration field {k} not recognized")

        self.normalize_address_unit(registration)

        vals = {
            "batch": "0",
            "united-states-citizen": "1",
            "eighteen-on-election-day": "1",
            "declaration1": "1",
        }
        for k in REQUIRED.keys():
            if k not in registration:
                raise InvalidRegistrationError(f"registration field {k} is required")

        for k, v in list(REQUIRED.items()) + list(OPTIONAL.items()):
            if k not in registration:
                continue
            if k == "date_of_birth":
                vals["DateOfBirth"] = registration[k].strftime("%Y-%m-%d")
            elif k == "party":
                party = registration[k].lower()
                if party in ["democrat"]:
                    party = "democratic"
                elif party.startswith("none"):
                    party = "none (no affiliation)"
                if party in PARTY:
                    vals["politicalparty"] = PARTY[party]
                else:
                    vals["politicalparty"] = PARTY["other"]
                    vals["otherpoliticalparty"] = party
            elif k == "gender":
                if registration[k] in GENDER:
                    vals[v] = GENDER[registration[k]]
                elif registration[k].upper() in GENDER.values():
                    vals[v] = registration[k].upper()
                else:
                    raise InvalidRegistrationError(f"gender '{v}' not recognized; must be one of {GENDER}")
            elif k == "suffix":
                # NOTE: the API enumerates specific suffixes; not sure what happens if we
                # submit one that is not listed.
                vals["TitleSuffix"] = registration[k]
            elif k == "federal_voter":
                vals["isfederalvoter"] = "1" if v else "0"
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

        if "dl_number" not in registration:
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
            ] = f"data:image/{signature_type};base64,{base64.b64encode(signature).decode('utf-8')}"

        root = etree.fromstring(XML_TEMPLATE)
        for record in root:
            for i in record:
                k = i.tag.split("}")[1]   # strip of "{xmlns}" prefix
                if k in vals:
                    i.text = vals[k]
        xml = etree.tostring(root).decode("utf-8")
        logger.debug(f"Submission: {json.dumps(xml)}")

        root = self.do_request("SETAPPLICATION", data=json.dumps({"ApplicationData": xml}))
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
