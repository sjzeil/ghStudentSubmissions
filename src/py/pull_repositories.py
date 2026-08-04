"""
Usage pull_repositories pathToCourseDirectory path_to_repos assignment [student1 student2 ...]

"""

import argparse
import logging
import os
import pprint as pp
import re
import subprocess
import sys
import time

from ghCourse import ghCourse
from GithubRepo import GithubRepo
    
SLEEP_AFTER_FETCH_OR_CLONE = 2

def parse_cli(args: list[str]):
    
    parser = argparse.ArgumentParser(
        # prog="upload_modules",
        description="Create a student repo as a copy of an instructor-supplied template"
    )
    parser.add_argument('coursePath', type=str, help='path to course directory')
    parser.add_argument('reposPath', type=str, help='path to collection of repos for all assignments')
    parser.add_argument('assignmentName', type=str, help='name of an assignment')
    parser.add_argument('students', type=str, nargs='*', help='optional list of students to create/pull repos for. If omitted, pulls all.')

    parsedArgs = parser.parse_args(args[1:])
    
    return parsedArgs

def student_has_pushed_anything(course: ghCourse, repoName: str) -> bool:
    g = GithubRepo(course.accessID, repoName)
    try:
        nCommits = g.numberOfCommits()
        return nCommits > 1
    except Exception as e:
        if 'Bad credentials' in str(e):
            organization = repoName.split('/')[0]
            logging.error(f"Error checking {repoName}: Bad credentials. Your Github access token may be invalid (for the GitHub organization {organization}) or expired.")
        else:
            logging.error(f"Error checking if student has pushed anything for repo {repoName}: {e}")
        return True  # If we can't access the repo via Github REST API, try to pull it anyway in case they have pushed.

def clone_repo(course: ghCourse, assignmentName: str, studentName: str, repoName: str, repoPath: str) -> bool:
    ssh_url = f"git@github.com:{repoName}.git"
    status = True
    try:
        command = ['git', 'clone', ssh_url, repoPath]
        result = subprocess.run(command, capture_output=True, text=True)
        if result.returncode != 0:
            logging.error(f"Error cloning repo {repoName} for student {studentName}: {result.stderr}")
            status = False
    except Exception as e:
        logging.error(f"Error cloning repo {repoName} for student {studentName}: {e}")
        status = False
    time.sleep(SLEEP_AFTER_FETCH_OR_CLONE)
    return status;


def get_last_commit_from_local_repo(repoPath) -> str:
    command = ['git', '-C', repoPath, 'rev-parse', 'HEAD']
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error getting last commit from local repo at {repoPath}: {result.stderr}")
        return 'should-not-match-anything'
    return result.stdout.strip()

def get_last_commit_from_github_repo(course: ghCourse, repoName: str) -> str:
    try:
        g = GithubRepo(course.accessID, repoName)
        return g.lastCommit()
    except Exception as e:
        if 'Bad credentials' in str(e):
            organization = repoName.split('/')[0]
            logging.error(f"Error getting last commit from Github repo {repoName}: Bad credentials. Your Github access token may be invalid (for the GitHub organization {organization}) or expired.")
        else:
            logging.error(f"Error getting last commit from Github repo {repoName}: {e}")
        return 'should_not_match_anything'

def pull_repo(studentName: str, repoPath: str) -> bool:
    status = True
    command = ['git', '-C', repoPath, 'pull']
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        logging.error(f"Error pulling repo for student {studentName} at {repoPath}: {result.stderr}")
        status = False
    time.sleep(SLEEP_AFTER_FETCH_OR_CLONE)
    return status

def pull_student_repos(course: ghCourse, assignmentName: str, students: list[str], reposPath: str):
    asstReposPath = os.path.join(reposPath, assignmentName)
    if not os.path.exists(asstReposPath):
        os.makedirs(asstReposPath)

    for repo in course.repositories:
        if (repo.assignment == assignmentName and (len(students) == 0 or repo.student in students)):
            repoPath = os.path.join(asstReposPath, repo.student)
            if not os.path.exists(repoPath):
                if student_has_pushed_anything(course, repo.repo):
                    OK = clone_repo(course, assignmentName, repo.student, repo.repo, repoPath)
                    if OK: 
                        logging.info(f"Cloned repo for student {repo.student}")
                    else:
                        logging.info(f"Clone failed for student {repo.student}")
                else:
                    logging.info(f"Student {repo.student} has not pushed anything yet.")
            else:
                hash1 = get_last_commit_from_local_repo(repoPath)
                hash2 = get_last_commit_from_github_repo(course, repo.repo)
                if hash1 == hash2:
                    logging.info(f"Local repo for student {repo.student} is already up to date.")
                else:
                    OK = pull_repo(repo.student, repoPath)
                    if OK:
                        logging.info(f"Pulled repo for student {repo.student}")
                    else:
                        logging.info(f"Pull failed for student {repo.student}")



def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("PyGithub").level = logging.ERROR
    
    args = parse_cli(sys.argv)
    
    course = ghCourse(args.coursePath)

    if not args.assignmentName in course.assignmentsByName:
        print(f"Error: assignment {args.assignmentName} not found in course described at {course.path}")
        sys.exit(1)

    pull_student_repos(course, args.assignmentName, args.students, args.reposPath)
    

if __name__ == "__main__":
    main()
