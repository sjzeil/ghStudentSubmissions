"""
Usage create_student_repo pathToCourseDirectory assignment csStudent 

"""

import argparse
import logging
import os
import pprint as pp
import re
import sys

from github import Github, Auth
from ghCourse import ghCourse
    

def parse_cli(args: list[str]):
    
    parser = argparse.ArgumentParser(
        # prog="upload_modules",
        description="Create a student repo as a copy of an instructor-supplied template"
    )
    parser.add_argument('coursePath', type=str, help='path to course directory')
    parser.add_argument('assignmentName', type=str, help='name of an assignment')
    parser.add_argument('student', type=str, help='name of student to create repo for')

    parsedArgs = parser.parse_args(args[1:])
    
    return parsedArgs

def create_student_repo(course: ghCourse, assignmentName: str, studentName: str) -> bool:
    if not course.checkAssignment(assignmentName):
        return False
    if not course.checkStudent(studentName):
        return False
    msg: str = course.createStudentRepo(assignmentName, studentName)
    print(msg)

    if not ('Error' in msg):
        course.save()
    return True
    

def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("PyGithub").level = logging.ERROR
    
    args = parse_cli(sys.argv)    
    
    course = ghCourse(args.coursePath)
    OK = create_student_repo(course, args.assignmentName, args.student)
    if not OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
