# This file is part of ts_criopy.
#
# Developed for the Vera C. Rubin Observatory Telescope and Site Systems.
# This product includes software developed by the LSST Project
# (https://www.lsst.org).
# See the COPYRIGHT file at the top-level directory of this distribution
# for details of code ownership.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import json
import os
from typing import Any

import pytest

CASSETTE_DIR = os.path.join(os.path.dirname(__file__), "cassettes")


def before_record_response(response: dict[str, Any]) -> dict[str, Any]:
    body_data = json.loads(response["body"]["string"].decode("utf-8"))

    for key in ["username", "password"]:
        if key in body_data:
            body_data[key] = "<secret>"

    response["body"]["string"] = json.dumps(body_data).encode("utf-8")

    return response


@pytest.fixture(scope="session")
def vcr_config() -> dict[str, Any]:
    return {
        "before_record_response": before_record_response,
        "cassette_library_dir": CASSETTE_DIR,
        "match_on": ["method", "scheme", "host", "port", "path", "query", "body"],
    }
