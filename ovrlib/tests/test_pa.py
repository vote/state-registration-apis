import pytest

from ..pa import Session


@pytest.mark.parametrize(
    "inaddr,outaddr",
    [
        (
            {"address1": "123 A st #456"},
            {"address1": "123 A st", "unittype": "UNIT", "unitnumber": "456"},
        ),
        (
            {"address1": "123 A st", "address2": "#456"},
            {"address1": "123 A st", "unittype": "UNIT", "unitnumber": "456"},
        ),
        (
            {"address1": "123 A st #456"},
            {"address1": "123 A st", "unittype": "UNIT", "unitnumber": "456"},
        ),
        (
            {"address1": "123 A st apt 456"},
            {"address1": "123 A st", "unittype": "APT", "unitnumber": "456"},
        ),
        (
            {"address1": "123 A st apt. 456"},
            {"address1": "123 A st", "unittype": "APT", "unitnumber": "456"},
        ),
        (
            {"address1": "123 A st", "address2": "apt. 456"},
            {"address1": "123 A st", "unittype": "APT", "unitnumber": "456"},
        ),
    ],
)
def test_normalize_address_unit(inaddr, outaddr):
    s = Session(api_key=None, staging=False)
    t = inaddr.copy()
    s.normalize_address_unit(t)
    assert t == outaddr
