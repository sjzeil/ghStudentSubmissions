import csv
import datetime as dt
from pathlib import Path

class Repository:
    assignmentName: str
    student: str
    repoName: str
    created: dt.datetime
    grade: int
    graded: dt.datetime

    def __init__(self, assignment: str, student: str, repoName: str, created: dt.datetime | None = None): 
        self.assignmentName = self.assignment
        self.student = student
        self.repoName = repoName
        self.grade = -1
        self.graded = None

        if created != None:
            self.created = created.astimezone()
        else:
            self.created = dt.now().astimezone()

        
class ghCourse:

    path: str
    accessID: str
    student2GHLogin: dict[str, str]
    ghLogin2Student: dict[str, str]
    asst2Template: dict[str, str]
    repositories: list[Repository]


    def __init__(self, path: str):
        self.path = path
        self.student2GHLogin = {}
        self.ghLogin2Student = {}
        self.repositories = []

        accessIDPath = f"{path}/.github"
        self.accessId = self._readAccessID(accessIDPath)

        if not Path.is_dir(Path(path)):
            raise FileNotFoundError(f"The directory {path} does not exist.")
        
        if Path.is_file(f"{path}/students.csv"):
            with open(f"{path}/students.csv", mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.student2GHLogin[row['CS Login']] = row['Github Login']
                    self.ghLogin2Student[row['Github Login']] = row['CS Login']

        if Path.is_file(f"{path}/templates.csv"):
            with open(f"{path}/templates.csv", mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.asst2Template[row['Assignment Name']] = row['Github Template']

        if Path.is_file(f"{path}/repositories.csv"):
            with open(f"{path}/repositories.csv", mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    createdDate = dt.fromisoformat(row['Created']).astimezone()
                    repo = Repository(row['Assignment'], row['CS Login'], row['Repository'], createdDate)
                    if row['Grade'] != None and row['Grade'] != '':
                        repo.grade = int(row['Grade'])
                    if row['Graded'] != None and row['Graded'] != '':
                        repo.graded = dt.fromisoformat(row['Graded']).astimezone()

    def _readAccessID(self, githubAccessIDFile: str) -> str:
        with open(githubAccessIDFile, 'r') as f:
            return f.read().strip()
