import csv
from dataclasses import dataclass, fields, asdict
import datetime as dt
from github import Github, Auth
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

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

    def createStudentRepo(self, asstName: str, studentLogin: str) -> str:

        if not (asstName in self.assignmentsByName):
            return f"Error: '{asstName}' has not been set up as an assignment."
        
        if not (studentLogin in self.studentsByName):
            return f"Error: '{studentLogin}' is not in the class or has not registered a Github account name."
        
        assignment: Assignment = self.assignmentsByName[asstName]
        student: Student = self.studentsByName[studentLogin]

        for repo in self.repositories:
            if (repo.assignment == assignment.name 
                and repo.student == student.local_name):
                return f"Student {student.local_name} has a repo for assignment {assignment.name} at https://github.com/{repo.repo}"


        github = Github(auth=Auth.Token(self.accessID))
        try:
            repoNameParts = assignment.template_repo.split('/')
            if len(repoNameParts) != 2:
                return (f"Error: Invalid template repo format: {assignment.template_repo}. Expected format: organization-name/repoName")
            organizationName, baseName = repoNameParts
            studentRepoName = f"{asstName}--{student.github_name}"
            organization = github.get_organization(organizationName)
            if self._repoAlreadyExists(organization, studentRepoName):
                return f"Error: Repository https://github.com/{organizationName}/{studentRepoName} already exists."
            templateRepo = organization.get_repo(repoNameParts[1])
            studentRepo = organization.create_repo_from_template(
                name=studentRepoName,
                repo=templateRepo,
                description=f"Created from template {assignment.template_repo}",
                private=True,
                include_all_branches=False,
                )
            # Now add the student as a collaborator to the new repo
            studentRepo.add_to_collaborators(student.github_name, permission=assignment.permissions)

            repo_description = Repository(asstName, studentLogin, f"{organizationName}/{studentRepoName}", dt.datetime.now())
            self.repositories.append(repo_description)

            return f"New repository created at https://github.com/{organizationName}/{studentRepoName}"
        except Exception as e:
            return f"Error: Unexpected error creating student repo for assignment {asstName}, student {studentLogin}: {e}"

    def _repoAlreadyExists(self, organization, repoName: str) -> bool:
        try:
            organization.get_repo(repoName)
            return True
        except Exception:
            return False
        
    def checkAssignment(self, name: str) -> bool:
        repository = ''
        try:
            repository = self.assignmentsByName[name]
        except:
            logging.error(f"'{name}' is not a known assignment name.")
            return False
        github = Github(auth=Auth.Token(self.accessID))
        try:
            organizationName, baseName = repository.template_repo.split('/')
            organization = github.get_organization(organizationName)
            repo = organization.get_repo(baseName)
        except Exception as e:
            logging.error(f"Error accessing template repo {repository.name} for assignment {name}: {e}")
            return False
        return True
    
    def checkStudent(self, name: str) -> bool:
        student = ''
        try:
            student = self.studentsByName[name]
        except:
            logging.error(f"'{name}' is not a known student name.")
            return False
        return self.checkGithubAccountName(student.github_name)
    
    def checkGithubAccountName(self, accountName: str) -> bool:
        github = Github(auth=Auth.Token(self.accessID))
        try:
            github.get_user(accountName)
            return True
        except:
            logger.error(f"'{accountName}' does not appear to be a valid Github account name.")
            return False
    
    def deleteRepository(self, assignment: str, student: str):
        for repo in self.repositories:
            if (repo.assignment == assignment and
                repo.student == student):
                repoName: str = repo.repo
                repoNameParts: list[str] = repoName.split('/')

                github = Github(auth=Auth.Token(self.accessID))
                organization = github.get_organization(repoNameParts[0])
                repository = organization.get_repo(repoNameParts[1])
                repository.delete()
                break
            
