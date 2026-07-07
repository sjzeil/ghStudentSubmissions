"""
Usage create_student_repo GitHubIDFile templateRepository studentGitHubAccount 

"""

import argparse
import logging
import os
import pprint as pp
import re
import sys


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
    msg: str = createStudentRepo(args.templateRepo, args.studentGithubAccount, accessID)
    print(msg)



if __name__ == "__main__":
    main()
