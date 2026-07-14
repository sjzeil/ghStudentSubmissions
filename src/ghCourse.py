import csv
from dataclasses import dataclass, fields, asdict
import datetime as dt
from pathlib import Path

@dataclass
class Repository:
    assignment: str
    student: str
    repo: str
    created: dt.datetime

@dataclass
class Student:
    local_name: str
    github_name: str

@dataclass
class Assignment:
    name: str
    template_repo: str
    permissions: str = 'push'
    teams: str = '' # individual assignment, not for teams

class ghCourse:

    path: str
    accessID: str
    studentsByName: dict[str, Student]
    assignmentsByName: dict[str, Assignment]
    repositories: list[Repository]


    def __init__(self, path: str):
        self.path = path
        self.studentsByName = {}
        self.ghLogin2Student = {}
        self.assignmentsByName = {}
        self.repositories = []

        accessIDPath = f"{path}/.github"
        self.accessID = self._readAccessID(accessIDPath)

        if not Path.is_dir(Path(path)):
            raise FileNotFoundError(f"The directory {path} does not exist.")
        
        if Path.is_file(Path(f"{path}/students.csv")):
            with open(f"{path}/students.csv", mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    student = Student(**row)
                    self.studentsByName[row['local_name']] = student

        if Path.is_file(Path(f"{path}/assignments.csv")):
            with open(f"{path}/assignments.csv", mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    asst = Assignment(**row)
                    self.assignmentsByName[row['name']] = asst

        if Path.is_file(Path(f"{path}/repositories.csv")):
            with open(f"{path}/repositories.csv", mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    createdDate = dt.datetime.fromisoformat(row['created']).astimezone()
                    row['created'] = createdDate
                    repo = Repository(**row)
                    self.repositories.append(repo)

    def _readAccessID(self, githubAccessIDFile: str) -> str:
        with open(githubAccessIDFile, 'r') as f:
            return f.read().strip()

    def save(self):
        with open(f"{self.path}/students.csv", mode='w', encoding='utf-8') as file:
            fieldNames = [f.name for f in fields(Student)]
            writer = csv.DictWriter(file, fieldnames=fieldNames)
            writer.writeheader()
            for repo in self.studentsByName.values():
                row = asdict(repo)
                writer.writerow(row)
            
        with open(f"{self.path}/assignments.csv", mode='w', encoding='utf-8') as file:
            fieldNames = [f.name for f in fields(Assignment)]
            writer = csv.DictWriter(file, fieldnames=fieldNames)
            writer.writeheader()
            for repo in self.assignmentsByName.values():
                row = asdict(repo)
                writer.writerow(row)

        with open(f"{self.path}/repositories.csv", mode='w', encoding='utf-8') as file:
            fieldNames = [f.name for f in fields(Repository)]
            writer = csv.DictWriter(file, fieldnames=fieldNames)
            writer.writeheader()
            for repo in self.repositories:
                row = asdict(repo)
                writer.writerow(row)
