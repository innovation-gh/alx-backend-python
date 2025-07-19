#!/usr/bin/env python3
"""Fixtures for integration tests."""

TEST_PAYLOAD = [
    (
        # org_payload
        {
            "login": "google",
            "id": 1342004,
            "node_id": "MDEyOk9yZ2FuaXphdGlvbjEzNDIwMDQ=",
            "url": "https://api.github.com/orgs/google",
            "repos_url": "https://api.github.com/orgs/google/repos",
            "events_url": "https://api.github.com/orgs/google/events",
            "hooks_url": "https://api.github.com/orgs/google/hooks",
            "issues_url": "https://api.github.com/orgs/google/issues",
            "members_url": "https://api.github.com/orgs/google/members{/member}",
            "public_members_url": "https://api.github.com/orgs/google/public_members{/member}",
            "avatar_url": "https://avatars1.githubusercontent.com/u/1342004?v=4",
            "description": "Google ❤️ Open Source",
        },
        # repos_payload
        [
            {
                "id": 7697149,
                "node_id": "MDEwOlJlcG9zaXRvcnk3Njk3MTQ5",
                "name": "episodes.dart",
                "full_name": "google/episodes.dart",
                "private": False,
                "owner": {
                    "login": "google",
                    "id": 1342004,
                },
                "html_url": "https://github.com/google/episodes.dart",
                "description": "A framework for timing performance  of web apps.",
                "fork": False,
                "url": "https://api.github.com/repos/google/episodes.dart",
            },
            {
                "id": 8566972,
                "node_id": "MDEwOlJlcG9zaXRvcnk4NTY2OTcy",
                "name": "kratu",
                "full_name": "google/kratu",
                "private": False,
                "owner": {
                    "login": "google",
                    "id": 1342004,
                },
                "html_url": "https://github.com/google/kratu",
                "description": "An JSON-stat library for JavaScript",
                "fork": False,
                "url": "https://api.github.com/repos/google/kratu",
            },
            {
                "id": 11126329,
                "node_id": "MDEwOlJlcG9zaXRvcnkxMTEyNjMyOQ==",
                "name": "build-debian-cloud",
                "full_name": "google/build-debian-cloud",
                "private": False,
                "owner": {
                    "login": "google",
                    "id": 1342004,
                },
                "html_url": "https://github.com/google/build-debian-cloud",
                "description": "",
                "fork": False,
                "url": "https://api.github.com/repos/google/build-debian-cloud",
                "license": {
                    "key": "apache-2.0",
                    "name": "Apache License 2.0",
                    "spdx_id": "Apache-2.0",
                    "url": "https://api.github.com/licenses/apache-2.0",
                    "node_id": "MDc6TGljZW5zZTI=",
                },
            },
        ],
        # expected_repos
        ["episodes.dart", "kratu", "build-debian-cloud"],
        # apache2_repos
        ["build-debian-cloud"],
    ),
]
