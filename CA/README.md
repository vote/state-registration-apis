# California

California has an API to allow you to pre-fill the state's OVR system. You'll send an API request to the state, and they'll reply with a token. You'll then redirect the user over to the state's OVR website with that token. The user can then skip filling out most of the information on the state's website.

 California can provide high-level, aggregated metrics on how many voters registered after you sent them to the state's website, but they don't provide individual-level data to track exactly which users completed the registration flow.

 ## Agreements and Restrictions

 California has a relatively strict set of requirements and agreements you must accept before you can use their system, or even receive a testing API key. We've included all of the documents we received from the state in this directory. You should review them very carefully before deciding to move forward.

 ## Process

1. Call the elections office at (916) 657-2166. Tell them you'd like to integrate with the state's OVR system. If the person you're talking to doesn't know what that means, ask to be transferred to a manager. You may need to leave a message with your email address. You should receive an email back within a few days from someone from the OVR office.

2. You'll be provided with the initial documentation, detailing the agreements you'll need to make with the state. If you're willing to move forward, you'll ask your point-of-contact to prepare a Memorandum of Understanding (MOU). Once the MOU is signed, you can access the test environment.

3. VoteAmerica decided not to move forward with this system, so we're not sure what comes next. If you do go down this route, please submit a PR with more information!
