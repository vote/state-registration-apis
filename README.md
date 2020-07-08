# State Registration APIs

This repo contains:

- VoteAmerica's documentation on how to work with states' online voter
registration system.

- ovrlib, a python library to interact with state APIs

## Background

Most states in the US provide online voter registration (OVR) systems (you can
find links to all of these systems in our
[Election Information API](https://docs.voteamerica.com/api/)).

If you are building a website or a system to direct voters to these registration
systems, a few states have gone beyond just letting you link to their OVR
website, and provide some additional capabilities:

- **Tracking Links**: Your organization can be issued a unique partner code.
Then, you pass this partner code in the URL parameters when directing voters
to the state OVR website. The state will then give you some information about
the voters who register using your link -- sometimes just aggregate statistics,
and sometimes individual voter file entries.

- **Prefilling Links**: If you already have some information about the voter,
some states will allow you to pre-fill some information about the voter so they
don't have to re-enter it on the state website. For some states, you'll just
pass this information in the URL parameters when sending them to the state OVR
site. For some states, you'll call the state's API with the pre-filled
information, get back a token from the state, and then pass that token in the
URL.

- **Full Registration API**: A small number of states offer full-features APIs
to submit voter registrations directly to the state. This means that voters
never need to leave your website -- they can enter in all their information
directly on your site, and you can submit the information to the state on their
behalf. Many of these APIs also support batch submissions -- so if you collect
voter information offline, you can submit that noninteractively. These APIs
tend to be complex, and the state usually has to review and approve your
website or application before you can use them.

## Challenges

While these tools are very useful, it's difficult to find good information on
them. Often, they're not mentioned on the state websites at all and you have
to know the right person to call or email about them. In addition, the APIs
often have tricky requirements or other challenging aspects to implement.

## This Repository

This repository is an attempt to make this process easier to navigate. It
includes:

- A listing of which states have systems you can integrate with
- Details instructions on how to get access to these systems -- who to call or
  email, what approvals you'll need, and how long it typically takes.
- ovrlib, a clean, readable Python library for interacting with the Full Registration
  APIs and the prefilling token APIs that you can use as-is, or read the source
  code of to understand how the systems work. For many of these systems, there
  are not official reference implementations so we are trying to provide good
  reference implementations here.

## A Word of Warning

While we do our best to keep this information up-to-date, this is not an
authoritative source. Any information you get from the states supersedes anything
in this repository. You are responsible for reading, understanding, and complying
with any agreements you make with the states while setting up these integrations.

We provide the software in this repository as-is, without
warranty of any kind, as laid out in the LICENSE file. While we hope that
the code in the repository is useful, you are ultimately responsible for any
systems you build using this code, and for complying with all local, state, and
federal regulations around election and voter registration systems.

# State Overviews

This table lists all the states with any sort of API or integration. You can
find a separate markdown file in this repository for each state with more
information.

| State | Integration Type | Process Documentation |
| --- | --- | --- |
| California | Prefilling Links via API call and token | [Docs](CA/README.md) |
| Colorado | Tracking Links (full voter file data) via URL Parameter | [Docs](CO/README.md) |
| Michigan | Full Registration API | TODO |
| Nevada | Tracking Links | TODO |
| Pennsylvania | Full Registration API | [Docs](PA/README.md)  |
| Virginia | Full Registration API | TODO |
| Washington | Tracking links (aggregate API) via URL parameter | [Docs](WA/README.md) |

## ovrlib

`ovrlib` is a python library for interacting with state's OVR APIs.
Currently, it only supports Pennsylvania. The source code is in [this repository](ovrlib/),
and the package is published on [PyPi](https://pypi.org/project/ovrlib/)

### Synopsis

```python
import ovrlib

session = ovrlib.pa.PAOVRSession(api_key=..., staging=True)
request = ovrlib.pa.PAOVRRequest(
    first_name="Sally",
    last_name="Penndot",
    suffix="XIV",
    date_of_birth=datetime.date(year=1944, month=5, day=2),
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
    is_new=True,
    dl_number="99007069",
)
response = session.register(req)
```

