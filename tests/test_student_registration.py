#!/usr/bin/python3
#
import csv
import datetime as dt
import logging
import os
import random
from pathlib import Path
import pytest
import shutil

from ghCourse import ghCourse, Assignment, Repository
from register_student import register_student

testCourse = 'build/testCourse'  

def setup():
    if Path.is_dir(Path(testCourse)):
        shutil.rmtree(testCourse)
    Path(testCourse).mkdir(parents=True, exist_ok=True)
    shutil.copytree('tests/data/course1', testCourse, dirs_exist_ok=True)


def test_new_student_registratioon():
    setup()
    course = ghCourse(testCourse)
    course.studentsByName.clear()
    course.save()
    
    newStudentName  = 'zeil'
    newGithubAccount = 'sjzeil'
    
    
    OK: bool = register_student(course, newStudentName, newGithubAccount)
    
    assert OK
    
    
    course2 = ghCourse(testCourse)
    
    recordedNewRepo = False
    assert newStudentName in course2.studentsByName
    assert course2.studentsByName[newStudentName].github_name == newGithubAccount

def test_existing_student_registration():
    setup()
    course = ghCourse(testCourse)
    
    newStudentName  = 'zeil'
    newGithubAccount = 'sjzeil'
    
    
    OK: bool = register_student(course, newStudentName, newGithubAccount)
    
    assert not OK
    
    
    course2 = ghCourse(testCourse)
    
    assert newStudentName in course2.studentsByName
    assert course2.studentsByName[newStudentName].github_name != newGithubAccount

def test_existing_student_registration2():
    setup()
    course = ghCourse(testCourse)
    
    newStudentName  = 'zeil'
    newGithubAccount = 'szeil'
    
    
    OK: bool = register_student(course, newStudentName, newGithubAccount)
    
    assert OK
    
    
    course2 = ghCourse(testCourse)
    
    assert newStudentName in course2.studentsByName
    assert course2.studentsByName[newStudentName].github_name == newGithubAccount

def test_github_account_reuse():
    setup()
    course = ghCourse(testCourse)
    
    newStudentName  = 'jones'
    newGithubAccount = 'szeil'
    
    
    OK: bool = register_student(course, newStudentName, newGithubAccount)
    
    assert not OK
    
    
    course2 = ghCourse(testCourse)
    
    assert not (newStudentName in course2.studentsByName)
