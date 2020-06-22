# Pennsylvania

Pennsylvania offers a full registration API: you can submit registrations
fully via the API without ever sending users to the state OVR website.

TODO: What tracking info do we get?

## Sign-Up Process

1. Sign up for a Keystone Login account:
   [https://keystonelogin.pa.gov/Account/Register](https://keystonelogin.pa.gov/Account/Register)
2. Using your Keystone Login, log into the OVR API site:
   [https://paovrwebapi.votespa.com/SUREWebAPIAdmin/Pages/Login](https://paovrwebapi.votespa.com/SUREWebAPIAdmin/Pages/Login)
3. When asked if you have an existing account, say No. You'll be taken the to API registration page.
4. After submitting your API registration, log back in and accept the terms of use (you might have to wait a bit before it will let you see the terms of use).
5. Wait for the elections office to email you with an approval. You'll get a read-only staging API key. They'll probably want to know your implementation timeline.
6. TODO: How to go from a read-only staging API key to a read-write staging API key.
7. Implement your website or application, using the staging API key.
8. Reply to the elections office to arrange for testing.
9. After you've completed testing, you'll be given a production API key and can go live.

## Additional Documentation

This folder contains all of the documentation we received from the state.
You should check with the state to make sure there aren't any newer versions
of these documents before you rely on them.
