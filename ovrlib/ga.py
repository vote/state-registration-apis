import datetime
import re
from dataclasses import dataclass
from typing import Optional

import requests

QUERY_ENDPOINT = "https://www.mvp.sos.ga.gov/MVP/voterDetails.do"

COUNTIES = {
    "APPLING": "001",
    "ATKINSON": "002",
    "BACON": "003",
    "BAKER": "004",
    "BALDWIN": "005",
    "BANKS": "006",
    "BARROW": "007",
    "BARTOW": "008",
    "BEN HILL": "009",
    "BERRIEN": "010",
    "BIBB": "011",
    "BLECKLEY": "012",
    "BRANTLEY": "013",
    "BROOKS": "014",
    "BRYAN": "015",
    "BULLOCH": "016",
    "BURKE": "017",
    "BUTTS": "018",
    "CALHOUN": "019",
    "CAMDEN": "020",
    "CANDLER": "021",
    "CARROLL": "022",
    "CATOOSA": "023",
    "CHARLTON": "024",
    "CHATHAM": "025",
    "CHATTAHOOCHEE": "026",
    "CHATTOOGA": "027",
    "CHEROKEE": "028",
    "CLARKE": "029",
    "CLAY": "030",
    "CLAYTON": "031",
    "CLINCH": "032",
    "COBB": "033",
    "COFFEE": "034",
    "COLQUITT": "035",
    "COLUMBIA": "036",
    "COOK": "037",
    "COWETA": "038",
    "CRAWFORD": "039",
    "CRISP": "040",
    "DADE": "041",
    "DAWSON": "042",
    "DECATUR": "043",
    "DEKALB": "044",
    "DODGE": "045",
    "DOOLY": "046",
    "DOUGHERTY": "047",
    "DOUGLAS": "048",
    "EARLY": "049",
    "ECHOLS": "050",
    "EFFINGHAM": "051",
    "ELBERT": "052",
    "EMANUEL": "053",
    "EVANS": "054",
    "FANNIN": "055",
    "FAYETTE": "056",
    "FLOYD": "057",
    "FORSYTH": "058",
    "FRANKLIN": "059",
    "FULTON": "060",
    "GILMER": "061",
    "GLASCOCK": "062",
    "GLYNN": "063",
    "GORDON": "064",
    "GRADY": "065",
    "GREENE": "066",
    "GWINNETT": "067",
    "HABERSHAM": "068",
    "HALL": "069",
    "HANCOCK": "070",
    "HARALSON": "071",
    "HARRIS": "072",
    "HART": "073",
    "HEARD": "074",
    "HENRY": "075",
    "HOUSTON": "076",
    "IRWIN": "077",
    "JACKSON": "078",
    "JASPER": "079",
    "JEFF DAVIS": "080",
    "JEFFERSON": "081",
    "JENKINS": "082",
    "JOHNSON": "083",
    "JONES": "084",
    "LAMAR": "085",
    "LANIER": "086",
    "LAURENS": "087",
    "LEE": "088",
    "LIBERTY": "089",
    "LINCOLN": "090",
    "LONG": "091",
    "LOWNDES": "092",
    "LUMPKIN": "093",
    "MACON": "094",
    "MADISON": "095",
    "MARION": "096",
    "MCDUFFIE": "097",
    "MCINTOSH": "098",
    "MERIWETHER": "099",
    "MILLER": "100",
    "MITCHELL": "101",
    "MONROE": "102",
    "MONTGOMERY": "103",
    "MORGAN": "104",
    "MURRAY": "105",
    "MUSCOGEE": "106",
    "NEWTON": "107",
    "OCONEE": "108",
    "OGLETHORPE": "109",
    "PAULDING": "110",
    "PEACH": "111",
    "PICKENS": "112",
    "PIERCE": "113",
    "PIKE": "114",
    "POLK": "115",
    "PULASKI": "116",
    "PUTNAM": "117",
    "QUITMAN": "118",
    "RABUN": "119",
    "RANDOLPH": "120",
    "RICHMOND": "121",
    "ROCKDALE": "122",
    "SCHLEY": "123",
    "SCREVEN": "124",
    "SEMINOLE": "125",
    "SPALDING": "126",
    "STEPHENS": "127",
    "STEWART": "128",
    "SUMTER": "129",
    "TALBOT": "130",
    "TALIAFERRO": "131",
    "TATTNALL": "132",
    "TAYLOR": "133",
    "TELFAIR": "134",
    "TERRELL": "135",
    "THOMAS": "136",
    "TIFT": "137",
    "TOOMBS": "138",
    "TOWNS": "139",
    "TREUTLEN": "140",
    "TROUP": "141",
    "TURNER": "142",
    "TWIGGS": "143",
    "UNION": "144",
    "UPSON": "145",
    "WALKER": "146",
    "WALTON": "147",
    "WARE": "148",
    "WARREN": "149",
    "WASHINGTON": "150",
    "WAYNE": "151",
    "WEBSTER": "152",
    "WHEELER": "153",
    "WHITE": "154",
    "WHITFIELD": "155",
    "WILCOX": "156",
    "WILKES": "157",
    "WILKINSON": "158",
    "WORTH": "159",
}


class GAInvalidCounty(Exception):
    pass


@dataclass
class GAVoterRegistration:
    full_name: str
    address: str
    city: str
    state: str
    zipcode: str

    date_of_birth: datetime.date

    status: str

    registration_date: datetime.date

    voter_reg_number: str  # NOTE: should this be an integer?

    @property
    def active(self):
        return self.status == "Active"

    @classmethod
    def from_page_source(cls, html, dob):
        html = html.replace("\n", " ")

        def get_span_value(spanid):
            m = re.search(f"<span id=['\"]{spanid}['\"]>([^<]*)</span>", html)
            if m:
                return m[1].strip()

        try:
            m = re.search(
                f'input type="hidden" name="idVoter" id="idVoter" value="(\d+)"/>', html
            )
            if m:
                voter_reg_number = m[1]
            else:
                return None
            reg_date = get_span_value("regDtSpan").split(": ")[1]
            address1 = get_span_value("resAddress1")
            address2 = get_span_value("resAddress2") or ""

            return GAVoterRegistration(
                full_name=get_span_value("fullNameSpan"),
                address=f"{address1} {address2}".strip(),
                city=get_span_value("resAddress3"),
                state=get_span_value("resAddress4").replace(",", "").strip(),
                zipcode=get_span_value("resAddress5").replace(",", "").strip(),
                date_of_birth=dob,
                status=get_span_value("statuscontent"),
                registration_date=datetime.datetime.strptime(
                    reg_date, "%m/%d/%Y"
                ).date(),
                voter_reg_number=voter_reg_number,
            )
        except Exception:
            return None


def lookup_voter(
    first_name: str, last_name: str, date_of_birth: datetime.date, county: str, **kwargs
) -> Optional[GAVoterRegistration]:
    county_id = COUNTIES.get(county.upper())
    if not county_id:
        raise GAInvalidCounty(f"{county} is not a recognized county")
    response = requests.post(
        QUERY_ENDPOINT,
        headers={"content-type": "application/x-www-form-urlencoded",},
        data={
            "firstName": first_name,
            "lastName": last_name,
            "dob": date_of_birth.strftime("%m/%d/%Y"),
            "county": county_id,
        },
        **kwargs,
    )
    if response.status_code != 200:
        return None

    return GAVoterRegistration.from_page_source(
        response.content.decode("utf-8"), date_of_birth
    )
