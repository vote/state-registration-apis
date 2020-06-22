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
5. The data file on the FTP server will be updated every day. You must pull the data daily, because each day's data file replaces the previous one. The file is updated around 4AM Mountain Time each day (if you are not in Colorado, be aware the the timestamps shown on the state FTP server's web UI are in Mountain Time and not your local timezone!). You should configure a system on your side to pull the file around 5AM Mountain Time every day. If you use [Civis](https://www.civisanalytics.com/), you can do this with the  "Multi from S/FTP to Civis" and "Import Multi from Civis" jobs to handle the ZIP file (the normal SFTP Civis import can't handle the ZIP file) -- you can reach out to Civis support for more information on these jobs.
