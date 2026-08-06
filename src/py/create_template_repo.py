"""
Usage create_template_repo pathToCourseDirectory organization assignment

"""

import argparse
import logging
import os
import pprint as pp
import re
import sys

from ghCourse import ghCourse
    

def parse_cli(args: list[str]):
    
    parser = argparse.ArgumentParser(
        # prog="upload_modules",
        description="Create a student repo as a copy of an instructor-supplied template"
    )
    parser.add_argument('coursePath', type=str, help='path to course directory')
    parser.add_argument('organization', type=str, help='name of GitHub organization')
    parser.add_argument('assignmentName', type=str, help='name of an assignment')

    parsedArgs = parser.parse_args(args[1:])
    
    return parsedArgs

def create_template_repo(course: ghCourse, assignmentName: str, organization: str) -> bool:
    if assignmentName in course.assignmentsByName:
        print(f"Assignment {assignmentName} already exists in course.")
        return False
    msg: str = course.createTemplateRepo(assignmentName, organization)
    print(msg)

    if not ('Error' in msg):
        course.save()
    return True
    

def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("PyGithub").level = logging.ERROR
    
    args = parse_cli(sys.argv)    
    
    course = ghCourse(args.coursePath)
    OK = create_template_repo(course, args.organization, args.assignmentName)
    if not OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
