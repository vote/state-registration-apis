from ovrlib.pa import PAOVRSession
import os

sess = PAOVRSession(os.environ["PA_OVR_KEY"], True)

print(sess.fetch_counties_and_municipalities())
