from loguru import logger
from yandex_tracker_client import TrackerClient

YANDEX_ORG_ID = 0
STARTREK_TOKEN_KEY_NAME = "startrek_token"


class PraktikTrackerClient(TrackerClient):
    def get_issues(self):
        filter_expression = {
            "queue": "PCR",
            "assignee": "me()",
        }
        logger.debug("Fetching issues...")
        issues = self.issues.find(filter=filter_expression)
        return sorted(issues, key=by_issue_key)


def get_startack_client(config) -> PraktikTrackerClient:
    if STARTREK_TOKEN_KEY_NAME not in config:
        logger.error(f"{STARTREK_TOKEN_KEY_NAME} top-level key not found in config 😿")
        exit(1)
    token = config[STARTREK_TOKEN_KEY_NAME]
    return PraktikTrackerClient(org_id=YANDEX_ORG_ID, base_url="https://st-api.yandex-team.ru", token=token)


# sorting keys


def by_issue_key(issue) -> int:
    key: str = issue.key  # e.g. PCR-12345
    assert key.startswith("PCR-")
    key_number_part = key.removeprefix("PCR-")
    key_number = int(key_number_part)
    return key_number