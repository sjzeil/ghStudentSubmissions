"""
Usage register_student.py pathToCourseDirectory local_student_name github_account_name

"""

import argparse
import logging
import os
import pprint as pp
import re
import sys

from github import Github, Auth
from ghCourse import ghCourse, Student
    

def parse_cli(args: list[str]):
    
    parser = argparse.ArgumentParser(
        # prog="upload_modules",
        description="Create a student repo as a copy of an instructor-supplied template"
    )
    parser.add_argument('coursePath', type=str, help='path to course directory')
    parser.add_argument('student', type=str, help='name of student to create repo for')
    parser.add_argument('githubAccount', type=str, help='Github account name for this student')
    
    parsedArgs = parser.parse_args(args[1:])
    
    return parsedArgs

def register_student(course: ghCourse, studentName: str, githubAccount: str) -> bool:
    if studentName in course.studentsByName:
        if githubAccount == course.studentsByName[studentName].github_name:
            print(f"Student {studentName} already registered as Github account {githubAccount}.")
            return True
        else:
            print(f"Error: Student {studentName} already registered as Github account {course.studentsByName[studentName].github_name}.")
            print("  Account can only be changed by permission of the instructor.")
            return False
        
            
    if not course.checkGithubAccountName(githubAccount):
        print(f"Error: '{githubAccount}' does not appear to be a valid Github account name.")
        return False
    
    for existingGithubAccount in course.studentsByName.values():
        if existingGithubAccount.github_name == githubAccount:
            print(f"Error: Github account '{githubAccount}' has already been registered to another student.")
            return False
    
    student = Student(studentName, githubAccount)
    course.studentsByName[studentName] = student
    course.save()
    
    return True
    

def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("PyGithub").level = logging.ERROR
    
    args = parse_cli(sys.argv)    
    
    course = ghCourse(args.coursePath)
    OK = register_student(course, args.student, args.githubAccount)
    if not OK:
        sys.exit(1)


if __name__ == "__main__":
    main()
