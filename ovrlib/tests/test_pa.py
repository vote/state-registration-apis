import datetime

import pytest  # type: ignore
import responses  # type: ignore
from responses import matchers

from ..pa import (
    STAGING_URL,
    PAOVRElectionInfo,
    PAOVRRequest,
    PAOVRSession,
    PACounty,
    PAMunicipality,
)


@pytest.mark.parametrize(
    "inaddr,outaddr",
    [
        (
            {"address1": "123 A st #456"},
            {"address1": "123 A st", "unit_type": "UNIT", "unit_number": "456"},
        ),
        (
            {"address1": "123 A st", "address2": "#456"},
            {"address1": "123 A st", "unit_type": "UNIT", "unit_number": "456"},
        ),
        (
            {"address1": "123 A st #456"},
            {"address1": "123 A st", "unit_type": "UNIT", "unit_number": "456"},
        ),
        (
            {"address1": "123 A st apt 456"},
            {"address1": "123 A st", "unit_type": "APT", "unit_number": "456"},
        ),
        (
            {"address1": "123 A st apt. 456"},
            {"address1": "123 A st", "unit_type": "APT", "unit_number": "456"},
        ),
        (
            {"address1": "123 A st", "address2": "apt. 456"},
            {"address1": "123 A st", "unit_type": "APT", "unit_number": "456"},
        ),
    ],
)
def test_normalize_address_unit(inaddr, outaddr):
    r = PAOVRRequest(
        first_name="",
        last_name="",
        date_of_birth=datetime.date(year=1, month=1, day=1),
        address1=inaddr.get("address1"),
        address2=inaddr.get("address2"),
        city="",
        county="",
        zipcode="",
        party="",
        united_states_citizen=True,
        eighteen_on_election_day=True,
        declaration=True,
        is_new=True,
    )
    r.normalize_address_unit()
    assert r.address1 == outaddr.get("address1")
    assert r.address2 == outaddr.get("address2")
    assert r.unit_type == outaddr.get("unit_type")
    assert r.unit_number == outaddr.get("unit_number")


@responses.activate
def test_simple():
    api_key = "abc"
    responses.add(
        responses.GET,
        STAGING_URL,
        match=[
            matchers.query_string_matcher(
                f"JSONv2&sysparm_AuthKey={api_key}&sysparm_action=GETERRORVALUES&sysparm_Language=0"
            )
        ],
        json="<OVRLookupData>  <MessageText>    <ErrorCode>VR_WAPI_InvalidAccessKey</ErrorCode>    <ErrorText>Access Key is Invalid.</ErrorText>  </MessageText></OVRLookupData>",
        status=200,
    )
    responses.add(
        responses.GET,
        STAGING_URL,
        match=[
            matchers.query_string_matcher(
                f"JSONv2&sysparm_AuthKey={api_key}&sysparm_action=GETAPPLICATIONSETUP&sysparm_Language=0"
            )
        ],
        json="<NewDataSet>  <Suffix>    <NameSuffixCode>II</NameSuffixCode>    <NameSuffixDescription>II</NameSuffixDescription>  </Suffix>  <Suffix>    <NameSuffixCode>III</NameSuffixCode>    <NameSuffixDescription>III</NameSuffixDescription>  </Suffix>  <Suffix>    <NameSuffixCode>IV</NameSuffixCode>    <NameSuffixDescription>IV</NameSuffixDescription>  </Suffix>  <Suffix>    <NameSuffixCode>JR</NameSuffixCode>    <NameSuffixDescription>JR</NameSuffixDescription>  </Suffix>  <Suffix>    <NameSuffixCode>SR</NameSuffixCode>    <NameSuffixDescription>SR</NameSuffixDescription>  </Suffix>  <Suffix>    <NameSuffixCode>V</NameSuffixCode>    <NameSuffixDescription>V</NameSuffixDescription>  </Suffix>  <Suffix>    <NameSuffixCode>VI</NameSuffixCode>    <NameSuffixDescription>VI</NameSuffixDescription>  </Suffix>  <Suffix>    <NameSuffixCode>VII</NameSuffixCode>    <NameSuffixDescription>VII</NameSuffixDescription>  </Suffix>  <Suffix>    <NameSuffixCode>I</NameSuffixCode>    <NameSuffixDescription>I</NameSuffixDescription>  </Suffix>  <Race>    <RaceCode>A</RaceCode>    <RaceDescription>ASIAN</RaceDescription>  </Race>  <Race>    <RaceCode>B</RaceCode>    <RaceDescription>BLACK OR AFRICAN AMERICAN</RaceDescription>  </Race>  <Race>    <RaceCode>H</RaceCode>    <RaceDescription>HISPANIC OR LATINO</RaceDescription>  </Race>  <Race>    <RaceCode>I</RaceCode>    <RaceDescription>NATIVE AMERICAN OR ALASKAN NATIVE</RaceDescription>  </Race>  <Race>    <RaceCode>P</RaceCode>    <RaceDescription>NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER</RaceDescription>  </Race>  <Race>    <RaceCode>O</RaceCode>    <RaceDescription>OTHER</RaceDescription>  </Race>  <Race>    <RaceCode>T</RaceCode>    <RaceDescription>TWO OR MORE RACES</RaceDescription>  </Race>  <Race>    <RaceCode>W</RaceCode>    <RaceDescription>WHITE</RaceDescription>  </Race>  <UnitTypes>    <UnitTypesCode>APT</UnitTypesCode>    <UnitTypesDescription>APARTMENT</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>BSM</UnitTypesCode>    <UnitTypesDescription>BASEMENT</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>BOX</UnitTypesCode>    <UnitTypesDescription>BOX #</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>BLD</UnitTypesCode>    <UnitTypesDescription>BUILDING</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>DEP</UnitTypesCode>    <UnitTypesDescription>DEPARTMENT</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>FL</UnitTypesCode>    <UnitTypesDescription>FLOOR</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>FRN</UnitTypesCode>    <UnitTypesDescription>FRONT</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>HNG</UnitTypesCode>    <UnitTypesDescription>HANGER</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>LBB</UnitTypesCode>    <UnitTypesDescription>LOBBY</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>LOT</UnitTypesCode>    <UnitTypesDescription>LOT</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>LOW</UnitTypesCode>    <UnitTypesDescription>LOWER</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>OFC</UnitTypesCode>    <UnitTypesDescription>OFFICE</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>PH</UnitTypesCode>    <UnitTypesDescription>PENTHOUSE</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>PIE</UnitTypesCode>    <UnitTypesDescription>PIER</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>POL</UnitTypesCode>    <UnitTypesDescription>POLL</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>REA</UnitTypesCode>    <UnitTypesDescription>REAR</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>RM</UnitTypesCode>    <UnitTypesDescription>ROOM</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>SID</UnitTypesCode>    <UnitTypesDescription>SIDE</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>SLI</UnitTypesCode>    <UnitTypesDescription>SLIP</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>SPC</UnitTypesCode>    <UnitTypesDescription>SPACE</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>STO</UnitTypesCode>    <UnitTypesDescription>STOP</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>STE</UnitTypesCode>    <UnitTypesDescription>SUITE</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>TRL</UnitTypesCode>    <UnitTypesDescription>TRAILER</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>UNI</UnitTypesCode>    <UnitTypesDescription>UNIT</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>UPP</UnitTypesCode>    <UnitTypesDescription>UPPER</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>TRLR</UnitTypesCode>    <UnitTypesDescription>TRAILER</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>CBN</UnitTypesCode>    <UnitTypesDescription>CABIN</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>HUB</UnitTypesCode>    <UnitTypesDescription>HUB</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>SMC</UnitTypesCode>    <UnitTypesDescription>STUDENT MAILING CENTER</UnitTypesDescription>  </UnitTypes>  <UnitTypes>    <UnitTypesCode>TH</UnitTypesCode>    <UnitTypesDescription>TOWNHOUSE</UnitTypesDescription>  </UnitTypes>  <AssistanceType>    <AssistanceTypeCode>HI</AssistanceTypeCode>    <AssistanceTypeDescription>I am deaf or hard of hearing</AssistanceTypeDescription>  </AssistanceType>  <AssistanceType>    <AssistanceTypeCode>VSI</AssistanceTypeCode>    <AssistanceTypeDescription>I am blind or have difficulty seeing</AssistanceTypeDescription>  </AssistanceType>  <AssistanceType>    <AssistanceTypeCode>WC</AssistanceTypeCode>    <AssistanceTypeDescription>I use a wheelchair</AssistanceTypeDescription>  </AssistanceType>  <AssistanceType>    <AssistanceTypeCode>PD</AssistanceTypeCode>    <AssistanceTypeDescription>I have a physical disability</AssistanceTypeDescription>  </AssistanceType>  <AssistanceType>    <AssistanceTypeCode>IL</AssistanceTypeCode>    <AssistanceTypeDescription>I need help reading</AssistanceTypeDescription>  </AssistanceType>  <AssistanceType>    <AssistanceTypeCode>LN</AssistanceTypeCode>    <AssistanceTypeDescription>I do not speak English well</AssistanceTypeDescription>  </AssistanceType>  <Gender>    <GenderCode>F</GenderCode>    <GenderDescription>Female</GenderDescription>  </Gender>  <Gender>    <GenderCode>M</GenderCode>    <GenderDescription>Male</GenderDescription>  </Gender>  <Gender>    <GenderCode>U</GenderCode>    <GenderDescription>Unknown</GenderDescription>  </Gender>  <PoliticalParty>    <PoliticalPartyCode>D</PoliticalPartyCode>    <PoliticalPartyDescription>Democratic</PoliticalPartyDescription>  </PoliticalParty>  <PoliticalParty>    <PoliticalPartyCode>R</PoliticalPartyCode>    <PoliticalPartyDescription>Republican</PoliticalPartyDescription>  </PoliticalParty>  <PoliticalParty>    <PoliticalPartyCode>GR</PoliticalPartyCode>    <PoliticalPartyDescription>Green</PoliticalPartyDescription>  </PoliticalParty>  <PoliticalParty>    <PoliticalPartyCode>LN</PoliticalPartyCode>    <PoliticalPartyDescription>Libertarian</PoliticalPartyDescription>  </PoliticalParty>  <PoliticalParty>    <PoliticalPartyCode>NF</PoliticalPartyCode>    <PoliticalPartyDescription>None (No Affiliation)</PoliticalPartyDescription>  </PoliticalParty>  <PoliticalParty>    <PoliticalPartyCode>OTH</PoliticalPartyCode>    <PoliticalPartyDescription>Other</PoliticalPartyDescription>  </PoliticalParty>  <Text_OVRApplnDeclaration>    <Text>&lt;p&gt;&lt;strong&gt;I declare that&lt;/strong&gt;&lt;/p&gt;&lt;ul&gt;&lt;li&gt;I am a United States citizen and will have been a citizen for at least 1 month on the day of the next election.&lt;/li&gt;&lt;li&gt;I will be at least 18 years old on the day of the next election.&lt;/li&gt;&lt;li&gt;I will have lived at the address in section 5 for at least 30 days before the election.&lt;/li&gt;&lt;li&gt;I am legally qualified to vote.&lt;/li&gt;&lt;/ul&gt;&lt;p&gt;I affirm that this information is true. I understand that this declaration is the same as an affidavit, and, if this information is not true, I can be convicted of perjury, and fined up to $15,000, jailed for up to 7 years, or both.&lt;/p&gt;&lt;p&gt;By checking the box below, you are signing the application electronically. In doing so:&lt;/p&gt;&lt;ul&gt;&lt;li&gt;You agree you have read and accept the terms of the declaration above.&lt;/li&gt;&lt;li&gt;You understand that your electronic signature on this application will constitute the legal equivalent of your signature for this voter registration application.&lt;/li&gt;&lt;li&gt;You agree to conduct this voter registration transaction by electronic means and that all laws of the Commonwealth of Pennsylvania will apply to this transaction.&lt;/li&gt;&lt;/ul&gt;\t&lt;p&gt;If you provided your PA driver's license or PennDOT ID number, you understand that the signature from the PennDOT record will constitute your signature on your voter registration record. If you upload an image of your signature, you understand that the signature you upload will constitute your signature on your voter registration record. You understand that you do not have to register electronically, and may use a paper or other non-electronic form of this voter registration application.&lt;/p&gt;</Text>  </Text_OVRApplnDeclaration>  <Text_OVRApplnAssistanceDeclaration>    <Text>&lt;p&gt;If you helped a voter complete this voter registration application, you must also sign the application.&lt;/p&gt;&lt;p&gt;By checking the box, you are signing the application electronically. In doing so:&lt;/p&gt;&lt;ul&gt;&lt;li&gt;You understand that your electronic signature on this application will constitute the legal equivalent of your signature.&lt;/li&gt;&lt;li&gt;You agree to sign this application by electronic means and that all laws of the Commonwealth of Pennsylvania will apply.&lt;/li&gt;&lt;/ul&gt;</Text>  </Text_OVRApplnAssistanceDeclaration>  <NextVRDeadline>    <NextVRDeadline>10/19/2020</NextVRDeadline>  </NextVRDeadline>  <NextElection>    <NextElection>11/03/2020</NextElection>  </NextElection>  <Text_OVRMailInApplnDeclaration>    <Text>&lt;p&gt;I declare that I am eligible to vote by mail-in ballot at the forthcoming primary or election; that I am requesting the ballot of the party with which I am enrolled according to my voter registration record and that all of the information which I have listed on this mail-in ballot application is true and correct.&lt;/p&gt;&lt;p&gt;&lt;strong&gt;WARNING:&lt;/strong&gt;If your mail-in ballot is received by the deadline, you will not be allowed to vote at your polling place.&lt;/p&gt;&lt;p&gt;By checking the box below, you are signing the application electronically. In doing so:&lt;/p&gt;&lt;ul&gt;&lt;li&gt;You agree you have read and accept the terms of the declaration above.&lt;/li&gt;&lt;li&gt;You understand that your electronic signature on this application will constitute a legal signature.&lt;/li&gt;&lt;li&gt;You agree to submit this mail-in ballot application electronically and that all laws of the Commonwealth of Pennsylvania will apply to this transaction.&lt;/li&gt;&lt;/ul&gt;&lt;p&gt;By providing your PA Driver's License or PennDOT ID number, you understand that the signature from that PennDOT record will count as your signature on your mail-in ballot application.&lt;/p&gt;</Text>  </Text_OVRMailInApplnDeclaration>  <Text_OVRMailInApplnComplDate>    <Text_OVRMailInApplnComplDate>10/27/2020</Text_OVRMailInApplnComplDate>  </Text_OVRMailInApplnComplDate>  <Text_OVRMailInBallotRecvdDate>    <Text_OVRMailInBallotRecvdDate>11/03/2020</Text_OVRMailInBallotRecvdDate>  </Text_OVRMailInBallotRecvdDate>  <MailinAddressTypes>    <MailinAddressTypesCode>R</MailinAddressTypesCode>    <MailinAddressTypesDescription>Residential Address</MailinAddressTypesDescription>  </MailinAddressTypes>  <MailinAddressTypes>    <MailinAddressTypesCode>M</MailinAddressTypesCode>    <MailinAddressTypesDescription>Mailing Address</MailinAddressTypesDescription>  </MailinAddressTypes>  <MailinAddressTypes>    <MailinAddressTypesCode>A</MailinAddressTypesCode>    <MailinAddressTypesDescription>Alternate Address</MailinAddressTypesDescription>  </MailinAddressTypes>  <Text_OVRMailInElectionName>    <ElectionName>2020 GENERAL ELECTION</ElectionName>  </Text_OVRMailInElectionName>  <Text_OVRMailInApplnComplTime>    <Time>5:00 PM</Time>  </Text_OVRMailInApplnComplTime>  <Text_OVRMailInBallotRecvdTime>    <RecvdTime>8:00 PM</RecvdTime>  </Text_OVRMailInBallotRecvdTime>  <County>    <countyID>0</countyID>    <Countyname />  </County>  <County>    <countyID>2290</countyID>    <Countyname>ADAMS</Countyname>  </County>  <County>    <countyID>2291</countyID>    <Countyname>ALLEGHENY</Countyname>  </County>  <County>    <countyID>2292</countyID>    <Countyname>ARMSTRONG</Countyname>  </County>  <County>    <countyID>2293</countyID>    <Countyname>BEAVER</Countyname>  </County>  <County>    <countyID>2294</countyID>    <Countyname>BEDFORD</Countyname>  </County>  <County>    <countyID>2295</countyID>    <Countyname>BERKS</Countyname>  </County>  <County>    <countyID>2296</countyID>    <Countyname>BLAIR</Countyname>  </County>  <County>    <countyID>2297</countyID>    <Countyname>BRADFORD</Countyname>  </County>  <County>    <countyID>2298</countyID>    <Countyname>BUCKS</Countyname>  </County>  <County>    <countyID>2299</countyID>    <Countyname>BUTLER</Countyname>  </County>  <County>    <countyID>2300</countyID>    <Countyname>CAMBRIA</Countyname>  </County>  <County>    <countyID>2301</countyID>    <Countyname>CAMERON</Countyname>  </County>  <County>    <countyID>2302</countyID>    <Countyname>CARBON</Countyname>  </County>  <County>    <countyID>2303</countyID>    <Countyname>CENTRE</Countyname>  </County>  <County>    <countyID>2304</countyID>    <Countyname>CHESTER</Countyname>  </County>  <County>    <countyID>2305</countyID>    <Countyname>CLARION</Countyname>  </County>  <County>    <countyID>2306</countyID>    <Countyname>CLEARFIELD</Countyname>  </County>  <County>    <countyID>2307</countyID>    <Countyname>CLINTON</Countyname>  </County>  <County>    <countyID>2308</countyID>    <Countyname>COLUMBIA</Countyname>  </County>  <County>    <countyID>2309</countyID>    <Countyname>CRAWFORD</Countyname>  </County>  <County>    <countyID>2310</countyID>    <Countyname>CUMBERLAND</Countyname>  </County>  <County>    <countyID>2311</countyID>    <Countyname>DAUPHIN</Countyname>  </County>  <County>    <countyID>2312</countyID>    <Countyname>DELAWARE</Countyname>  </County>  <County>    <countyID>2313</countyID>    <Countyname>ELK</Countyname>  </County>  <County>    <countyID>2314</countyID>    <Countyname>ERIE</Countyname>  </County>  <County>    <countyID>2315</countyID>    <Countyname>FAYETTE</Countyname>  </County>  <County>    <countyID>2316</countyID>    <Countyname>FOREST</Countyname>  </County>  <County>    <countyID>2317</countyID>    <Countyname>FRANKLIN</Countyname>  </County>  <County>    <countyID>2318</countyID>    <Countyname>FULTON</Countyname>  </County>  <County>    <countyID>2319</countyID>    <Countyname>GREENE</Countyname>  </County>  <County>    <countyID>2320</countyID>    <Countyname>HUNTINGDON</Countyname>  </County>  <County>    <countyID>2321</countyID>    <Countyname>INDIANA</Countyname>  </County>  <County>    <countyID>2322</countyID>    <Countyname>JEFFERSON</Countyname>  </County>  <County>    <countyID>2323</countyID>    <Countyname>JUNIATA</Countyname>  </County>  <County>    <countyID>2324</countyID>    <Countyname>LACKAWANNA</Countyname>  </County>  <County>    <countyID>2325</countyID>    <Countyname>LANCASTER</Countyname>  </County>  <County>    <countyID>2326</countyID>    <Countyname>LAWRENCE</Countyname>  </County>  <County>    <countyID>2327</countyID>    <Countyname>LEBANON</Countyname>  </County>  <County>    <countyID>2328</countyID>    <Countyname>LEHIGH</Countyname>  </County>  <County>    <countyID>2329</countyID>    <Countyname>LUZERNE</Countyname>  </County>  <County>    <countyID>2330</countyID>    <Countyname>LYCOMING</Countyname>  </County>  <County>    <countyID>2331</countyID>    <Countyname>MCKEAN</Countyname>  </County>  <County>    <countyID>2332</countyID>    <Countyname>MERCER</Countyname>  </County>  <County>    <countyID>2333</countyID>    <Countyname>MIFFLIN</Countyname>  </County>  <County>    <countyID>2334</countyID>    <Countyname>MONROE</Countyname>  </County>  <County>    <countyID>2335</countyID>    <Countyname>MONTGOMERY</Countyname>  </County>  <County>    <countyID>2336</countyID>    <Countyname>MONTOUR</Countyname>  </County>  <County>    <countyID>2337</countyID>    <Countyname>NORTHAMPTON</Countyname>  </County>  <County>    <countyID>2338</countyID>    <Countyname>NORTHUMBERLAND</Countyname>  </County>  <County>    <countyID>2339</countyID>    <Countyname>PERRY</Countyname>  </County>  <County>    <countyID>2340</countyID>    <Countyname>PHILADELPHIA</Countyname>  </County>  <County>    <countyID>2341</countyID>    <Countyname>PIKE</Countyname>  </County>  <County>    <countyID>2342</countyID>    <Countyname>POTTER</Countyname>  </County>  <County>    <countyID>2343</countyID>    <Countyname>SCHUYLKILL</Countyname>  </County>  <County>    <countyID>2344</countyID>    <Countyname>SNYDER</Countyname>  </County>  <County>    <countyID>2345</countyID>    <Countyname>SOMERSET</Countyname>  </County>  <County>    <countyID>2346</countyID>    <Countyname>SULLIVAN</Countyname>  </County>  <County>    <countyID>2347</countyID>    <Countyname>SUSQUEHANNA</Countyname>  </County>  <County>    <countyID>2348</countyID>    <Countyname>TIOGA</Countyname>  </County>  <County>    <countyID>2349</countyID>    <Countyname>UNION</Countyname>  </County>  <County>    <countyID>2350</countyID>    <Countyname>VENANGO</Countyname>  </County>  <County>    <countyID>2351</countyID>    <Countyname>WARREN</Countyname>  </County>  <County>    <countyID>2352</countyID>    <Countyname>WASHINGTON</Countyname>  </County>  <County>    <countyID>2353</countyID>    <Countyname>WAYNE</Countyname>  </County>  <County>    <countyID>2354</countyID>    <Countyname>WESTMORELAND</Countyname>  </County>  <County>    <countyID>2355</countyID>    <Countyname>WYOMING</Countyname>  </County>  <County>    <countyID>2356</countyID>    <Countyname>YORK</Countyname>  </County>  <States>    <Code>AL</Code>    <CodesDescription>Alabama</CodesDescription>  </States>  <States>    <Code>AK</Code>    <CodesDescription>Alaska</CodesDescription>  </States>  <States>    <Code>AS</Code>    <CodesDescription>American Samoa</CodesDescription>  </States>  <States>    <Code>AZ</Code>    <CodesDescription>Arizona</CodesDescription>  </States>  <States>    <Code>AR</Code>    <CodesDescription>Arkansas</CodesDescription>  </States>  <States>    <Code>AE</Code>    <CodesDescription>Armed Forces Africa, Armed Forces Canada, Armed Fo</CodesDescription>  </States>  <States>    <Code>AA</Code>    <CodesDescription>Armed Forces America (except Canada)</CodesDescription>  </States>  <States>    <Code>AP</Code>    <CodesDescription>Armed Forces Pacific</CodesDescription>  </States>  <States>    <Code>CA</Code>    <CodesDescription>California</CodesDescription>  </States>  <States>    <Code>CO</Code>    <CodesDescription>Colorado</CodesDescription>  </States>  <States>    <Code>CT</Code>    <CodesDescription>Connecticut</CodesDescription>  </States>  <States>    <Code>DE</Code>    <CodesDescription>Delaware</CodesDescription>  </States>  <States>    <Code>DC</Code>    <CodesDescription>District Of Columbia</CodesDescription>  </States>  <States>    <Code>FM</Code>    <CodesDescription>Federated States of Micronesia</CodesDescription>  </States>  <States>    <Code>FL</Code>    <CodesDescription>Florida</CodesDescription>  </States>  <States>    <Code>GA</Code>    <CodesDescription>Georgia</CodesDescription>  </States>  <States>    <Code>GU</Code>    <CodesDescription>Guam</CodesDescription>  </States>  <States>    <Code>HI</Code>    <CodesDescription>Hawaii</CodesDescription>  </States>  <States>    <Code>ID</Code>    <CodesDescription>Idaho</CodesDescription>  </States>  <States>    <Code>IL</Code>    <CodesDescription>Illinois</CodesDescription>  </States>  <States>    <Code>IN</Code>    <CodesDescription>Indiana</CodesDescription>  </States>  <States>    <Code>IA</Code>    <CodesDescription>Iowa</CodesDescription>  </States>  <States>    <Code>KS</Code>    <CodesDescription>Kansas</CodesDescription>  </States>  <States>    <Code>KY</Code>    <CodesDescription>Kentucky</CodesDescription>  </States>  <States>    <Code>LA</Code>    <CodesDescription>Louisiana</CodesDescription>  </States>  <States>    <Code>ME</Code>    <CodesDescription>Maine</CodesDescription>  </States>  <States>    <Code>MH</Code>    <CodesDescription>Marshall Islands</CodesDescription>  </States>  <States>    <Code>MD</Code>    <CodesDescription>Maryland</CodesDescription>  </States>  <States>    <Code>MA</Code>    <CodesDescription>Massachusetts</CodesDescription>  </States>  <States>    <Code>MI</Code>    <CodesDescription>Michigan</CodesDescription>  </States>  <States>    <Code>MN</Code>    <CodesDescription>Minnesota</CodesDescription>  </States>  <States>    <Code>MS</Code>    <CodesDescription>Mississippi</CodesDescription>  </States>  <States>    <Code>MO</Code>    <CodesDescription>Missouri</CodesDescription>  </States>  <States>    <Code>MT</Code>    <CodesDescription>Montana</CodesDescription>  </States>  <States>    <Code>NE</Code>    <CodesDescription>Nebraska</CodesDescription>  </States>  <States>    <Code>NV</Code>    <CodesDescription>Nevada</CodesDescription>  </States>  <States>    <Code>NH</Code>    <CodesDescription>New Hampshire</CodesDescription>  </States>  <States>    <Code>NJ</Code>    <CodesDescription>New Jersey</CodesDescription>  </States>  <States>    <Code>NM</Code>    <CodesDescription>New Mexico</CodesDescription>  </States>  <States>    <Code>NY</Code>    <CodesDescription>New York</CodesDescription>  </States>  <States>    <Code>NC</Code>    <CodesDescription>North Carolina</CodesDescription>  </States>  <States>    <Code>ND</Code>    <CodesDescription>North Dakota</CodesDescription>  </States>  <States>    <Code>MP</Code>    <CodesDescription>Northern Mariana Islands</CodesDescription>  </States>  <States>    <Code>OH</Code>    <CodesDescription>Ohio</CodesDescription>  </States>  <States>    <Code>OK</Code>    <CodesDescription>Oklahoma</CodesDescription>  </States>  <States>    <Code>OR</Code>    <CodesDescription>Oregon</CodesDescription>  </States>  <States>    <Code>PW</Code>    <CodesDescription>Palau</CodesDescription>  </States>  <States>    <Code>PA</Code>    <CodesDescription>Pennsylvania</CodesDescription>  </States>  <States>    <Code>PR</Code>    <CodesDescription>Puerto Rico</CodesDescription>  </States>  <States>    <Code>RI</Code>    <CodesDescription>Rhode Island</CodesDescription>  </States>  <States>    <Code>SC</Code>    <CodesDescription>South Carolina</CodesDescription>  </States>  <States>    <Code>SD</Code>    <CodesDescription>South Dakota</CodesDescription>  </States>  <States>    <Code>TN</Code>    <CodesDescription>Tennessee</CodesDescription>  </States>  <States>    <Code>TX</Code>    <CodesDescription>Texas</CodesDescription>  </States>  <States>    <Code>VI</Code>    <CodesDescription>US Virgin Islands</CodesDescription>  </States>  <States>    <Code>UT</Code>    <CodesDescription>Utah</CodesDescription>  </States>  <States>    <Code>VT</Code>    <CodesDescription>Vermont</CodesDescription>  </States>  <States>    <Code>VA</Code>    <CodesDescription>Virginia</CodesDescription>  </States>  <States>    <Code>WA</Code>    <CodesDescription>Washington</CodesDescription>  </States>  <States>    <Code>WV</Code>    <CodesDescription>West Virginia</CodesDescription>  </States>  <States>    <Code>WI</Code>    <CodesDescription>Wisconsin</CodesDescription>  </States>  <States>    <Code>WY</Code>    <CodesDescription>Wyoming</CodesDescription>  </States></NewDataSet>",
        status=200,
    )
    responses.add(
        responses.GET,
        STAGING_URL,
        match=[
            matchers.query_string_matcher(
                f"JSONv2&sysparm_AuthKey={api_key}&sysparm_action=GETXMLTEMPLATE&sysparm_Language=0"
            )
        ],
        json="<APIOnlineApplicationData xmlns='OVRexternaldata'>  <record>    <batch></batch>    <FirstName></FirstName>    <MiddleName></MiddleName>    <LastName></LastName>    <TitleSuffix></TitleSuffix>    <united-states-citizen></united-states-citizen>    <eighteen-on-election-day></eighteen-on-election-day>    <isnewregistration></isnewregistration>    <name-update></name-update>    <address-update></address-update>    <ispartychange></ispartychange>    <isfederalvoter></isfederalvoter>    <DateOfBirth></DateOfBirth>    <Gender></Gender>    <Ethnicity></Ethnicity>    <Phone></Phone>    <Email></Email>    <streetaddress></streetaddress>    <streetaddress2></streetaddress2>    <unittype></unittype>    <unitnumber></unitnumber>    <city></city>    <zipcode></zipcode>    <donthavePermtOrResAddress></donthavePermtOrResAddress>    <county></county>    <municipality></municipality>    <mailingaddress></mailingaddress>    <mailingcity></mailingcity>    <mailingstate></mailingstate>    <mailingzipcode></mailingzipcode>    <drivers-license></drivers-license>    <ssn4></ssn4>    <signatureimage></signatureimage>    <continueAppSubmit></continueAppSubmit>    <donthavebothDLandSSN></donthavebothDLandSSN>    <politicalparty></politicalparty>    <otherpoliticalparty></otherpoliticalparty>    <needhelptovote></needhelptovote>    <typeofassistance></typeofassistance>    <preferredlanguage></preferredlanguage>    <voterregnumber></voterregnumber>    <previousreglastname></previousreglastname>    <previousregfirstname></previousregfirstname>    <previousregmiddlename></previousregmiddlename>    <previousregaddress></previousregaddress>    <previousregcity></previousregcity>    <previousregstate></previousregstate>    <previousregzip></previousregzip>    <previousregcounty></previousregcounty>    <previousregyear></previousregyear>    <declaration1></declaration1>    <assistedpersonname></assistedpersonname>    <assistedpersonAddress></assistedpersonAddress>    <assistedpersonphone></assistedpersonphone>    <assistancedeclaration2></assistancedeclaration2>    <ispollworker></ispollworker>    <bilingualinterpreter></bilingualinterpreter>    <pollworkerspeaklang></pollworkerspeaklang>    <secondEmail></secondEmail>    <ismailin></ismailin>    <istransferpermanent></istransferpermanent>    <mailinaddresstype></mailinaddresstype>    <mailinballotaddr></mailinballotaddr>    <mailincity></mailincity>    <mailinstate></mailinstate>    <mailinzipcode></mailinzipcode>    <mailinward></mailinward>    <mailinlivedsince></mailinlivedsince>    <mailindeclaration></mailindeclaration>  </record></APIOnlineApplicationData>",
        status=200,
    )

    s = PAOVRSession(api_key="abc", staging=True)
    r = s.fetch_constants()

    assert len(responses.calls) == 3
    assert r == {
        "error": {"VR_WAPI_InvalidAccessKey": "Access Key is Invalid."},
        "county": {
            "adams": "2290",
            "allegheny": "2291",
            "armstrong": "2292",
            "beaver": "2293",
            "bedford": "2294",
            "berks": "2295",
            "blair": "2296",
            "bradford": "2297",
            "bucks": "2298",
            "butler": "2299",
            "cambria": "2300",
            "cameron": "2301",
            "carbon": "2302",
            "centre": "2303",
            "chester": "2304",
            "clarion": "2305",
            "clearfield": "2306",
            "clinton": "2307",
            "columbia": "2308",
            "crawford": "2309",
            "cumberland": "2310",
            "dauphin": "2311",
            "delaware": "2312",
            "elk": "2313",
            "erie": "2314",
            "fayette": "2315",
            "forest": "2316",
            "franklin": "2317",
            "fulton": "2318",
            "greene": "2319",
            "huntingdon": "2320",
            "indiana": "2321",
            "jefferson": "2322",
            "juniata": "2323",
            "lackawanna": "2324",
            "lancaster": "2325",
            "lawrence": "2326",
            "lebanon": "2327",
            "lehigh": "2328",
            "luzerne": "2329",
            "lycoming": "2330",
            "mckean": "2331",
            "mercer": "2332",
            "mifflin": "2333",
            "monroe": "2334",
            "montgomery": "2335",
            "montour": "2336",
            "northampton": "2337",
            "northumberland": "2338",
            "perry": "2339",
            "philadelphia": "2340",
            "pike": "2341",
            "potter": "2342",
            "schuylkill": "2343",
            "snyder": "2344",
            "somerset": "2345",
            "sullivan": "2346",
            "susquehanna": "2347",
            "tioga": "2348",
            "union": "2349",
            "venango": "2350",
            "warren": "2351",
            "washington": "2352",
            "wayne": "2353",
            "westmoreland": "2354",
            "wyoming": "2355",
            "york": "2356",
        },
        "suffix": {},
        "state": {
            "alabama": "AL",
            "alaska": "AK",
            "american samoa": "AS",
            "arizona": "AZ",
            "arkansas": "AR",
            "armed forces africa, armed forces canada, armed fo": "AE",
            "armed forces america (except canada)": "AA",
            "armed forces pacific": "AP",
            "california": "CA",
            "colorado": "CO",
            "connecticut": "CT",
            "delaware": "DE",
            "district of columbia": "DC",
            "federated states of micronesia": "FM",
            "florida": "FL",
            "georgia": "GA",
            "guam": "GU",
            "hawaii": "HI",
            "idaho": "ID",
            "illinois": "IL",
            "indiana": "IN",
            "iowa": "IA",
            "kansas": "KS",
            "kentucky": "KY",
            "louisiana": "LA",
            "maine": "ME",
            "marshall islands": "MH",
            "maryland": "MD",
            "massachusetts": "MA",
            "michigan": "MI",
            "minnesota": "MN",
            "mississippi": "MS",
            "missouri": "MO",
            "montana": "MT",
            "nebraska": "NE",
            "nevada": "NV",
            "new hampshire": "NH",
            "new jersey": "NJ",
            "new mexico": "NM",
            "new york": "NY",
            "north carolina": "NC",
            "north dakota": "ND",
            "northern mariana islands": "MP",
            "ohio": "OH",
            "oklahoma": "OK",
            "oregon": "OR",
            "palau": "PW",
            "pennsylvania": "PA",
            "puerto rico": "PR",
            "rhode island": "RI",
            "south carolina": "SC",
            "south dakota": "SD",
            "tennessee": "TN",
            "texas": "TX",
            "us virgin islands": "VI",
            "utah": "UT",
            "vermont": "VT",
            "virginia": "VA",
            "washington": "WA",
            "west virginia": "WV",
            "wisconsin": "WI",
            "wyoming": "WY",
        },
        "party": {
            "democratic": "D",
            "republican": "R",
            "green": "GR",
            "libertarian": "LN",
            "none (no affiliation)": "NF",
            "other": "OTH",
        },
        "gender": {"female": "F", "male": "M", "unknown": "U"},
        "race": {
            "ii": "II",
            "iii": "III",
            "iv": "IV",
            "jr": "JR",
            "sr": "SR",
            "v": "V",
            "vi": "VI",
            "vii": "VII",
            "i": "I",
            "asian": "A",
            "black or african american": "B",
            "hispanic or latino": "H",
            "native american or alaskan native": "I",
            "native hawaiian or other pacific islander": "P",
            "other": "O",
            "two or more races": "T",
            "white": "W",
        },
        "unit_type": {
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
        },
        "assistance_type": {
            "I am deaf or hard of hearing": "HI",
            "I am blind or have difficulty seeing": "VSI",
            "I use a wheelchair": "WC",
            "I have a physical disability": "PD",
            "I need help reading": "IL",
            "I do not speak English well": "LN",
        },
        "xml_template": "<APIOnlineApplicationData xmlns='OVRexternaldata'>  <record>    <batch></batch>    <FirstName></FirstName>    <MiddleName></MiddleName>    <LastName></LastName>    <TitleSuffix></TitleSuffix>    <united-states-citizen></united-states-citizen>    <eighteen-on-election-day></eighteen-on-election-day>    <isnewregistration></isnewregistration>    <name-update></name-update>    <address-update></address-update>    <ispartychange></ispartychange>    <isfederalvoter></isfederalvoter>    <DateOfBirth></DateOfBirth>    <Gender></Gender>    <Ethnicity></Ethnicity>    <Phone></Phone>    <Email></Email>    <streetaddress></streetaddress>    <streetaddress2></streetaddress2>    <unittype></unittype>    <unitnumber></unitnumber>    <city></city>    <zipcode></zipcode>    <donthavePermtOrResAddress></donthavePermtOrResAddress>    <county></county>    <municipality></municipality>    <mailingaddress></mailingaddress>    <mailingcity></mailingcity>    <mailingstate></mailingstate>    <mailingzipcode></mailingzipcode>    <drivers-license></drivers-license>    <ssn4></ssn4>    <signatureimage></signatureimage>    <continueAppSubmit></continueAppSubmit>    <donthavebothDLandSSN></donthavebothDLandSSN>    <politicalparty></politicalparty>    <otherpoliticalparty></otherpoliticalparty>    <needhelptovote></needhelptovote>    <typeofassistance></typeofassistance>    <preferredlanguage></preferredlanguage>    <voterregnumber></voterregnumber>    <previousreglastname></previousreglastname>    <previousregfirstname></previousregfirstname>    <previousregmiddlename></previousregmiddlename>    <previousregaddress></previousregaddress>    <previousregcity></previousregcity>    <previousregstate></previousregstate>    <previousregzip></previousregzip>    <previousregcounty></previousregcounty>    <previousregyear></previousregyear>    <declaration1></declaration1>    <assistedpersonname></assistedpersonname>    <assistedpersonAddress></assistedpersonAddress>    <assistedpersonphone></assistedpersonphone>    <assistancedeclaration2></assistancedeclaration2>    <ispollworker></ispollworker>    <bilingualinterpreter></bilingualinterpreter>    <pollworkerspeaklang></pollworkerspeaklang>    <secondEmail></secondEmail>    <ismailin></ismailin>    <istransferpermanent></istransferpermanent>    <mailinaddresstype></mailinaddresstype>    <mailinballotaddr></mailinballotaddr>    <mailincity></mailincity>    <mailinstate></mailinstate>    <mailinzipcode></mailinzipcode>    <mailinward></mailinward>    <mailinlivedsince></mailinlivedsince>    <mailindeclaration></mailindeclaration>  </record></APIOnlineApplicationData>",
    }

    r = s.get_election_info()
    assert r == PAOVRElectionInfo(
        next_election="11/03/2020",
        next_vr_deadline="10/19/2020",
        vr_declaration="<p><strong>I declare that</strong></p><ul><li>I am a United States citizen and will have been a citizen for at least 1 month on the day of the next election.</li><li>I will be at least 18 years old on the day of the next election.</li><li>I will have lived at the address in section 5 for at least 30 days before the election.</li><li>I am legally qualified to vote.</li></ul><p>I affirm that this information is true. I understand that this declaration is the same as an affidavit, and, if this information is not true, I can be convicted of perjury, and fined up to $15,000, jailed for up to 7 years, or both.</p><p>By checking the box below, you are signing the application electronically. In doing so:</p><ul><li>You agree you have read and accept the terms of the declaration above.</li><li>You understand that your electronic signature on this application will constitute the legal equivalent of your signature for this voter registration application.</li><li>You agree to conduct this voter registration transaction by electronic means and that all laws of the Commonwealth of Pennsylvania will apply to this transaction.</li></ul>\t<p>If you provided your PA driver's license or PennDOT ID number, you understand that the signature from the PennDOT record will constitute your signature on your voter registration record. If you upload an image of your signature, you understand that the signature you upload will constitute your signature on your voter registration record. You understand that you do not have to register electronically, and may use a paper or other non-electronic form of this voter registration application.</p>",
        vbm_election_name="2020 GENERAL ELECTION",
        vbm_request_deadline=datetime.datetime(2020, 10, 27, 17, 0),
        vbm_request_declaration="<p>I declare that I am eligible to vote by mail-in ballot at the forthcoming primary or election; that I am requesting the ballot of the party with which I am enrolled according to my voter registration record and that all of the information which I have listed on this mail-in ballot application is true and correct.</p><p><strong>WARNING:</strong>If your mail-in ballot is received by the deadline, you will not be allowed to vote at your polling place.</p><p>By checking the box below, you are signing the application electronically. In doing so:</p><ul><li>You agree you have read and accept the terms of the declaration above.</li><li>You understand that your electronic signature on this application will constitute a legal signature.</li><li>You agree to submit this mail-in ballot application electronically and that all laws of the Commonwealth of Pennsylvania will apply to this transaction.</li></ul><p>By providing your PA Driver's License or PennDOT ID number, you understand that the signature from that PennDOT record will count as your signature on your mail-in ballot application.</p>",
        vbm_receipt_deadline=datetime.datetime(2020, 11, 3, 20, 0),
    )


@pytest.mark.parametrize(
    "reg,body",
    [
        (
            PAOVRRequest(
                first_name="Sally",
                last_name="Penndot",
                suffix="XIV",
                date_of_birth=datetime.date(1944, 5, 2),
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
                dl_number="99007069",
                is_new=True,
            ),
            '{"ApplicationData": "<APIOnlineApplicationData xmlns=\\"OVRexternaldata\\">  <record>    <batch>0</batch>    <FirstName>Sally</FirstName>    <MiddleName/>    <LastName>Penndot</LastName>    <TitleSuffix>XIV</TitleSuffix>    <united-states-citizen>1</united-states-citizen>    <eighteen-on-election-day>1</eighteen-on-election-day>    <isnewregistration>1</isnewregistration>    <name-update/>    <address-update/>    <ispartychange/>    <isfederalvoter>1</isfederalvoter>    <DateOfBirth>1944-05-02</DateOfBirth>    <Gender/>    <Ethnicity/>    <Phone/>    <Email/>    <streetaddress>123 A St</streetaddress>    <streetaddress2/>    <unittype/>    <unitnumber/>    <city>Clarion</city>    <zipcode>16214</zipcode>    <donthavePermtOrResAddress/>    <county>Clarion</county>    <municipality/>    <mailingaddress/>    <mailingcity/>    <mailingstate/>    <mailingzipcode/>    <drivers-license>99007069</drivers-license>    <ssn4/>    <signatureimage/>    <continueAppSubmit/>    <donthavebothDLandSSN/>    <politicalparty>D</politicalparty>    <otherpoliticalparty/>    <needhelptovote/>    <typeofassistance/>    <preferredlanguage/>    <voterregnumber/>    <previousreglastname/>    <previousregfirstname/>    <previousregmiddlename/>    <previousregaddress/>    <previousregcity/>    <previousregstate/>    <previousregzip/>    <previousregcounty/>    <previousregyear/>    <declaration1>1</declaration1>    <assistedpersonname/>    <assistedpersonAddress/>    <assistedpersonphone/>    <assistancedeclaration2/>    <ispollworker/>    <bilingualinterpreter/>    <pollworkerspeaklang/>    <secondEmail/>    <ismailin/>    <istransferpermanent/>    <mailinaddresstype/>    <mailinballotaddr/>    <mailincity/>    <mailinstate/>    <mailinzipcode/>    <mailinward/>    <mailinlivedsince/>    <mailindeclaration/>  </record></APIOnlineApplicationData>"}',
        ),
    ],
)
def test_register_prepare_body(reg, body):
    out = reg.to_request_body()
    assert out == body


@responses.activate
def test_get_counties():
    api_key = "abc"
    responses.add(
        responses.GET,
        STAGING_URL,
        match=[
            matchers.query_string_matcher(
                f"JSONv2&sysparm_AuthKey={api_key}&sysparm_action=GETAPPLICATIONSETUP&sysparm_Language=0"
            )
        ],
        json="<NewDataSet>  <County>    <countyID>0</countyID>    <Countyname />  </County>  <County>    <countyID>2290</countyID>    <Countyname>ADAMS</Countyname>  </County>  <County>    <countyID>2291</countyID>    <Countyname>ALLEGHENY</Countyname>  </County> </NewDataSet>",
        status=200,
    )
    responses.add(
        responses.GET,
        STAGING_URL,
        match=[
            matchers.query_string_matcher(
                f"JSONv2&sysparm_AuthKey={api_key}&sysparm_action=GETERRORVALUES&sysparm_Language=0"
            )
        ],
        json="<OVRLookupData>  <MessageText>    <ErrorCode>VR_WAPI_InvalidAccessKey</ErrorCode>    <ErrorText>Access Key is Invalid.</ErrorText>  </MessageText></OVRLookupData>",
        status=200,
    )
    responses.add(
        responses.GET,
        STAGING_URL,
        match=[
            matchers.query_string_matcher(
                f"JSONv2&sysparm_AuthKey={api_key}&sysparm_action=GETXMLTEMPLATE&sysparm_Language=0"
            )
        ],
        json="<APIOnlineApplicationData xmlns='OVRexternaldata'>  <record>    <batch></batch>    <FirstName></FirstName>    <MiddleName></MiddleName>    <LastName></LastName>    <TitleSuffix></TitleSuffix>    <united-states-citizen></united-states-citizen>    <eighteen-on-election-day></eighteen-on-election-day>    <isnewregistration></isnewregistration>    <name-update></name-update>    <address-update></address-update>    <ispartychange></ispartychange>    <isfederalvoter></isfederalvoter>    <DateOfBirth></DateOfBirth>    <Gender></Gender>    <Ethnicity></Ethnicity>    <Phone></Phone>    <Email></Email>    <streetaddress></streetaddress>    <streetaddress2></streetaddress2>    <unittype></unittype>    <unitnumber></unitnumber>    <city></city>    <zipcode></zipcode>    <donthavePermtOrResAddress></donthavePermtOrResAddress>    <county></county>    <municipality></municipality>    <mailingaddress></mailingaddress>    <mailingcity></mailingcity>    <mailingstate></mailingstate>    <mailingzipcode></mailingzipcode>    <drivers-license></drivers-license>    <ssn4></ssn4>    <signatureimage></signatureimage>    <continueAppSubmit></continueAppSubmit>    <donthavebothDLandSSN></donthavebothDLandSSN>    <politicalparty></politicalparty>    <otherpoliticalparty></otherpoliticalparty>    <needhelptovote></needhelptovote>    <typeofassistance></typeofassistance>    <preferredlanguage></preferredlanguage>    <voterregnumber></voterregnumber>    <previousreglastname></previousreglastname>    <previousregfirstname></previousregfirstname>    <previousregmiddlename></previousregmiddlename>    <previousregaddress></previousregaddress>    <previousregcity></previousregcity>    <previousregstate></previousregstate>    <previousregzip></previousregzip>    <previousregcounty></previousregcounty>    <previousregyear></previousregyear>    <declaration1></declaration1>    <assistedpersonname></assistedpersonname>    <assistedpersonAddress></assistedpersonAddress>    <assistedpersonphone></assistedpersonphone>    <assistancedeclaration2></assistancedeclaration2>    <ispollworker></ispollworker>    <bilingualinterpreter></bilingualinterpreter>    <pollworkerspeaklang></pollworkerspeaklang>    <secondEmail></secondEmail>    <ismailin></ismailin>    <istransferpermanent></istransferpermanent>    <mailinaddresstype></mailinaddresstype>    <mailinballotaddr></mailinballotaddr>    <mailincity></mailincity>    <mailinstate></mailinstate>    <mailinzipcode></mailinzipcode>    <mailinward></mailinward>    <mailinlivedsince></mailinlivedsince>    <mailindeclaration></mailindeclaration>  </record></APIOnlineApplicationData>",
        status=200,
    )
    responses.add(
        responses.GET,
        STAGING_URL,
        match=[
            matchers.query_string_matcher(
                f"JSONv2&sysparm_AuthKey={api_key}&sysparm_action=GETMUNICIPALITIES&sysparm_Language=0&sysparm_County=ADAMS"
            )
        ],
        json="<OVRLookupData>  <Municipality>    <MunicipalityType>0</MunicipalityType>    <MunicipalityID/>    <MunicipalityIDname/>    <CountyID>0</CountyID>    <CountyName/>  </Municipality>  <Municipality>    <MunicipalityType>4</MunicipalityType>    <MunicipalityID>BR1</MunicipalityID>    <MunicipalityIDname>ABBOTTSTOWN</MunicipalityIDname>    <CountyID>2290</CountyID>    <CountyName>ADAMS</CountyName>  </Municipality>  <Municipality>    <MunicipalityType>4</MunicipalityType>    <MunicipalityID>BR2</MunicipalityID>    <MunicipalityIDname>ARENDTSVILLE</MunicipalityIDname>    <CountyID>2290</CountyID>    <CountyName>ADAMS</CountyName>  </Municipality>  </OVRLookupData>",
        status=200,
    )
    responses.add(
        responses.GET,
        STAGING_URL,
        match=[
            matchers.query_string_matcher(
                f"JSONv2&sysparm_AuthKey={api_key}&sysparm_action=GETMUNICIPALITIES&sysparm_Language=0&sysparm_County=ALLEGHENY"
            )
        ],
        json="<OVRLookupData>  <Municipality>    <MunicipalityType>0</MunicipalityType>    <MunicipalityID/>    <MunicipalityIDname/>    <CountyID>0</CountyID>    <CountyName/>  </Municipality>  <Municipality>    <MunicipalityType>4</MunicipalityType>    <MunicipalityID>MN101</MunicipalityID>    <MunicipalityIDname>ALEPPO</MunicipalityIDname>    <CountyID>2291</CountyID>    <CountyName>ALLEGHENY</CountyName>  </Municipality>  <Municipality>    <MunicipalityType>4</MunicipalityType>    <MunicipalityID>MN102</MunicipalityID>    <MunicipalityIDname>ASPINWALL</MunicipalityIDname>    <CountyID>2291</CountyID>    <CountyName>ALLEGHENY</CountyName>  </Municipality></OVRLookupData>",
        status=200,
    )

    s = PAOVRSession(api_key="abc", staging=True)
    r = s.fetch_counties_and_municipalities()

    assert len(responses.calls) == 5
    assert r == [
        PACounty(
            county_id="2290",
            county_name="ADAMS",
            municipalities=[
                PAMunicipality(municipality_id="BR1", municipality_name="ABBOTTSTOWN"),
                PAMunicipality(municipality_id="BR2", municipality_name="ARENDTSVILLE"),
            ],
        ),
        PACounty(
            county_id="2291",
            county_name="ALLEGHENY",
            municipalities=[
                PAMunicipality(municipality_id="MN101", municipality_name="ALEPPO"),
                PAMunicipality(municipality_id="MN102", municipality_name="ASPINWALL"),
            ],
        ),
    ]
