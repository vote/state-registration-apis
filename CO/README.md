# Colorado

Colorado can issue you an Online Voter Registration Drive (OLVRD) ID. You can
pass this OLVRD ID in the URL parameters when sending voters to Colorado's OVR
website. As part of the registration process, you'll receive an FTP login.
You can use this FTP login to get a daily CSV with all the information about
people who have registered using your registration link. This CSV includes
full voter file data: names, years of birth, etc.

You can learn more about the system from [this brochure](https://www.sos.state.co.us/pubs/elections/VoterRegDrive/files/OnlineVRDBrochure.pdf)

## Process

1. Go to [https://www.sos.state.co.us/pubs/elections/VoterRegDrive/VRDhome.html](https://www.sos.state.co.us/pubs/elections/VoterRegDrive/VRDhome.html) and register as a Voter Registration Drive. You'll need to make an account, take the online training class, and pass an online test.
2. After passing the test, fill out [https://www.sos.state.co.us/pubs/elections/VoterRegDrive/files/VRDIntent.pdf](https://www.sos.state.co.us/pubs/elections/VoterRegDrive/files/VRDIntent.pdf) and email it to vrd@sos.state.co.us. Make sure to check the box in section 5. Note that you will need to have an "Agent", who must be a resident of Colorado -- they won't need to do anything, they just need to be listed on the paperwork.
3. You'll hear back from the VRD office within a few days with your acceptance. You'll be given a unique URL to send voters to, and a login to the state FTP server to pull the voter registration data.
4. 1-3 days later, you'll receive an email with your FTP login credentials. You'll receive two separate emails: one with your username and one with your password. The password may not work -- if that happens, you can use the "reset password" link on the login screen and provide your username to get a reset-password email and create a working password.

## The OVR Link

Once you've been approved by the VRD office, you'll get a URL to send voters to that looks like this: `https://www.sos.state.co.us/voter?vrdid=999999999` (where `999999999` is the VRD ID you've been issued by the state).

There's a couple things you can do with this link:

- You can add a `campaign`, like this: `https://www.sos.state.co.us/voter?vrdid=999999999&campaign=some-id-here`. You can use whatever ID you want for the campaign, and the data you get back from the state will have the campaign ID associated with the record for the voter. At VoteAmerica, for example, we use a unique ID that we can correlate back to the user's session on our website.

- You can also link directly to the voter reigstration page (the default link goes to the voter registration portal, which has a bunch of options other than registering to vote), like this: `https://www.sos.state.co.us/voter/pages/pub/olvr/verifyNewVoter.xhtml?vrdid=999999999` (again, `999999999` is the VRD ID you've been issued). The tracking and data will work just the same.

## Importing the Data

The data file on the FTP server will be updated every day. The data is provide as a file called `VRD_REPORT.zip`, which is a ZIP archive containing a single `VRD_REPORT.txt` file. This is a tab-separated values file (like a CSV, but with tabs instead of commas).

You must pull the data daily, because each day's data file replaces the previous one. The file is updated around 4AM Mountain Time each day (if you are not in Colorado, be aware the the timestamps shown on the state FTP server's web UI are in Mountain Time and not your local timezone!).

You should configure a system on your side to pull the file around 5AM Mountain Time every day. If you use [Civis](https://www.civisanalytics.com/), you can do this with the  "Multi from S/FTP to Civis" and "Import Multi from Civis" jobs to handle the ZIP file (the normal SFTP Civis import can't handle the ZIP file) -- you can reach out to Civis support for more information on these jobs.
