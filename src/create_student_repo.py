"""
Usage create_student_repo GitHubAccessIDFile course assignment csStudent 

"""

import argparse
import logging
import os
import pprint as pp
import re
import sys

from github import Github, Auth
    

def readAccessID(githubAccessIDFile: str) -> str:
    with open(githubAccessIDFile, 'r') as f:
        return f.read().strip()

def checkTemplateRepo(templateRepo: str, accessID: str):
    github = Github(auth=Auth.Token(accessID))
    try:
        repo = github.get_repo(templateRepo)
    except Exception as e:
        print(f"Error accessing template repo {templateRepo}: {e}")
        logging.error(f"Error accessing template repo {templateRepo}: {e}")
        sys.exit(1)

def checkStudentAccountName(studentAccountName: str, accessID: str):
    github = Github(auth=Auth.Token(accessID))
    try:
        user = github.get_user(studentAccountName)
    except Exception as e:
        print(f"Error: apparently invalid student account name {studentAccountName}: {e}")
        logging.error(f"Error: apparently invalid student account name {studentAccountName}: {e}")
        sys.exit(1)

def repoAlreadyExists(organization, repoName: str) -> bool:
    try:
        organization.get_repo(repoName)
        return True
    except Exception:
        return False

def createStudentRepo(accessID: str, coursePath: str, asstName: str, studentLogin: str, ) -> str:
    github = Github(auth=Auth.Token(accessID))
    try:
        template = github.get_repo(templateRepoName)
        repoNameParts = templateRepoName.split('/')
        if len(repoNameParts) != 2:
            return (f"Error: Invalid template repo format: {templateRepoName}. Expected format: organization-name/repoName")
        organizationName, baseName = repoNameParts
        studentRepoName = f"{baseName}-{studentGithubAccount}"
        organization = github.get_organization(organizationName)
        if repoAlreadyExists(organization, studentRepoName):
            return f"Repository https://github.com/{organizationName}/{studentRepoName} already exists."
        templateRepo = organization.get_repo(repoNameParts[1])
        studentRepo = organization.create_repo_from_template(
            name=studentRepoName,
            repo=templateRepo,
            description=f"Created from template {templateRepoName}",
            private=True,
            include_all_branches=False,
        )
        # Now add the student as a collaborator to the new repo
        studentRepo.add_to_collaborators(studentGithubAccount, permission='push')

        return f"New repository created at https://github.com/{organizationName}/{studentRepoName}"
    except Exception as e:
        return f"Error creating student repo for {studentGithubAccount}: {e}"

def parse_cli(args: list[str]):
    global replacing, summarize, gradedActivities, reviewActivities, assignmentActivities, generateSyllabus
    
    parser = argparse.ArgumentParser(
        # prog="upload_modules",
        description="Create a student repo as a copy of an instructor-supplied template"
    )
    parser.add_argument('githubAccessID', type=str, help='path to file with access ID for member of course organization')
    parser.add_argument('templateRepo', type=str, help='template rpo in form organization-name/repoName')
    parser.add_argument('studentGithubAccount', type=str, help='name of student GitHub account to create repo for')

    parsedArgs = parser.parse_args(args[1:])
    
    githubAccessID = parsedArgs.githubAccessID
    templateRepo = parsedArgs.templateRepo
    studentGithubAccount = parsedArgs.studentGithubAccount
    
    return parsedArgs


def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("PyGithub").level = logging.ERROR
    
    args = parse_cli(sys.argv)    
    
    accessID: str = readAccessID(args.githubAccessID)
    checkTemplateRepo(args.templateRepo, accessID)
    checkStudentAccountName(args.studentGithubAccount, accessID)
    msg: str = createStudentRepo(args.templateRepo, args.studentGithubAccount, accessID)
    print(msg)



if __name__ == "__main__":
    main()
