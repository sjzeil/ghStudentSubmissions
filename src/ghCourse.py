import csv
import datetime as dt
from pathlib import Path

class Repository:
    assignmentName: str
    student: str
    repoName: str
    created: dt.datetime

    def __init__(self, assignment: str, student: str, repoName: str, created: dt.datetime | None = None): 
        self.assignmentName = assignment
        self.student = student
        self.repoName = repoName

        if created != None:
            self.created = created.astimezone()
        else:
            self.created = dt.datetime.now().astimezone()

        
class ghCourse:

    path: str
    accessID: str
    student2GHLogin: dict[str, str]
    ghLogin2Student: dict[str, str]
    asst2Template: dict[str, str]
    repositories: list[Repository]

    studentsFieldNames = ['CS Login', 'Github Login']
    templatesFieldNames = ['Assignment Name', 'Github Template']
    repositoriesFieldNames = ['Assignment', 'CS Login', 'Repository', 'Created']

    def __init__(self, path: str):
        self.path = path
        self.student2GHLogin = {}
        self.ghLogin2Student = {}
        self.asst2Template = {}
        self.repositories = []

        accessIDPath = f"{path}/.github"
        self.accessID = self._readAccessID(accessIDPath)

        if not Path.is_dir(Path(path)):
            raise FileNotFoundError(f"The directory {path} does not exist.")
        
        if Path.is_file(Path(f"{path}/students.csv")):
            with open(f"{path}/students.csv", mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.student2GHLogin[row['CS Login']] = row['Github Login']
                    self.ghLogin2Student[row['Github Login']] = row['CS Login']

        if Path.is_file(Path(f"{path}/templates.csv")):
            with open(f"{path}/templates.csv", mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    self.asst2Template[row['Assignment Name']] = row['Github Template']

        if Path.is_file(Path(f"{path}/repositories.csv")):
            with open(f"{path}/repositories.csv", mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    createdDate = dt.datetime.fromisoformat(row['Created']).astimezone()
                    repo = Repository(row['Assignment'], row['CS Login'], row['Repository'], createdDate)
                    self.repositories.append(repo)

    def _readAccessID(self, githubAccessIDFile: str) -> str:
        with open(githubAccessIDFile, 'r') as f:
            return f.read().strip()

    def save(self):
        with open(f"{self.path}/students.csv", mode='w', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(ghCourse.studentsFieldNames)
            for student, ghLogin in self.student2GHLogin:
                row = [student, ghLogin]
                writer.writerow(row)
            
            