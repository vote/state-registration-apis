# Pennsylvania

Pennsylvania offers a full registration API: you can submit registrations
fully via the API without ever sending users to the state OVR website.

## Sign-Up Process

1. Sign up for a Keystone Login account:
   [https://keystonelogin.pa.gov/Account/Register](https://keystonelogin.pa.gov/Account/Register)
2. Using your Keystone Login, log into the OVR API site:
   [https://paovrwebapi.votespa.com/SUREWebAPIAdmin/Pages/Login](https://paovrwebapi.votespa.com/SUREWebAPIAdmin/Pages/Login)
3. When asked if you have an existing account, say No. You'll be taken the to API registration page.
4. After submitting your API registration, log back in and accept the terms of use (you might have to wait a bit before it will let you see the terms of use).
5. Wait for the elections office to email you with an approval. You'll get a read-only staging API key. They'll probably want to know your implementation timeline.
6. You'll probably want to get your API key upgrading to a read-write staging API key (by default, they only give you a read-only staging API key). To do this, just email the elections office back and ask for read-write staging access.
7. Implement your website or application, using the staging API key.
8. Reply to the elections office to arrange for testing.
9. After you've completed testing, you'll be given a production API key and can go live.

## Additional Documentation

This folder contains all of the documentation we received from the state.
You should check with the state to make sure there aren't any newer versions
of these documents before you rely on them.

## Sample API request

Here's a cURL request you can use to hit the API. Make sure to replace `$YOUR_API_KEY` with your read-write staging API key. It will submit `input.json` as a body:

```bash
curl -H 'Content-Type: application/json' \
-H 'Cache-Control: no-cache' \
--data-binary @input.json \
"https://paovrwebapi.beta.votespa.com/SureOVRWebAPI/api/ovr?JSONv2&sysparm_AuthKey=$YOUR_API_KEY&sysparm_action=SETAPPLICATION&sysparm_Language=0"
```

And here's the `input.json` file:

```json
{"ApplicationData":"<APIOnlineApplicationData xmlns=\"OVRexternaldata\"><record><batch>0</batch><FirstName>Sally</FirstName><MiddleName></MiddleName><LastName>Penndot</LastName><TitleSuffix></TitleSuffix><united-states-citizen>1</united-states-citizen><eighteen-on-election-day>1</eighteen-on-election-day><isnewregistration>1</isnewregistration><name-update>0</name-update><address-update>0</address-update><ispartychange>0</ispartychange><isfederalvoter>0</isfederalvoter><DateOfBirth>1944-05-02</DateOfBirth><Gender></Gender><Ethnicity></Ethnicity><Phone></Phone><Email></Email><streetaddress>328 South St</streetaddress><streetaddress2></streetaddress2><unittype></unittype><unitnumber></unitnumber><city>Clarion</city><zipcode>16214</zipcode><donthavePermtOrResAddress>0</donthavePermtOrResAddress><county>ADAMS</county><municipality>Clarion</municipality><mailingaddress></mailingaddress><mailingcity></mailingcity><mailingstate></mailingstate><mailingzipcode></mailingzipcode><drivers-license>99007069</drivers-license><ssn4>0451</ssn4><signatureimage></signatureimage><continueAppSubmit>1</continueAppSubmit><donthavebothDLandSSN>0</donthavebothDLandSSN><politicalparty>D</politicalparty><otherpoliticalparty></otherpoliticalparty><needhelptovote>0</needhelptovote><typeofassistance></typeofassistance><preferredlanguage>en</preferredlanguage><voterregnumber></voterregnumber><previousreglastname></previousreglastname><previousregfirstname></previousregfirstname><previousregmiddlename></previousregmiddlename><previousregaddress></previousregaddress><previousregcity></previousregcity><previousregstate></previousregstate><previousregzip></previousregzip><previousregcounty></previousregcounty><previousregyear></previousregyear><declaration1>1</declaration1><assistedpersonname></assistedpersonname><assistedpersonAddress></assistedpersonAddress><assistedpersonphone></assistedpersonphone><assistancedeclaration2></assistancedeclaration2><ispollworker>0</ispollworker><bilingualinterpreter></bilingualinterpreter><pollworkerspeaklang></pollworkerspeaklang><secondEmail></secondEmail></record></APIOnlineApplicationData>"}
```
