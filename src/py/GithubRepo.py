import csv
from dataclasses import dataclass, fields, asdict
import datetime as dt
import logging
import requests
from pathlib import Path

logger = logging.getLogger(__name__)

class GithubRepo:

    accessID: str
    name: str


    def __init__(self, access_ID: str, repoName: str = ''):
        self.accessID = access_ID
        self.name = repoName
        self.commits = None

    def setName(self, repoName: str):
        self.name = repoName
        self.commits = None


    def _fetch_commits(self):
        if self.commits is not None:
            return self.commits

        url = f"https://api.github.com/repos/{self.name}/commits"
        headers = {
            "Authorization": f"Bearer {self.accessID}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            self.commits = response.json()
        else:
            logger.error(f"Failed to fetch commits for repository {self.name}: {response.status_code} {response.text}")
        
    def numberOfCommits(self) -> int:
        if self.commits is None:
            self._fetch_commits()
        return len(self.commits) if self.commits is not None else 0

    def lastCommit(self) -> str:
        if self.commits is None:
            self._fetch_commits()
        if self.commits and len(self.commits) > 0:
            return self.commits[0]['sha']
        else:
            return 'should-not-match-anything'

