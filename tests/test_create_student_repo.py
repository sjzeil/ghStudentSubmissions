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
from create_student_repo import create_student_repo

testCourse = 'build/testCourse'  

def setup():
    if Path.is_dir(Path(testCourse)):
        shutil.rmtree(testCourse)
    Path(testCourse).mkdir(parents=True, exist_ok=True)
    shutil.copytree('tests/data/course1', testCourse, dirs_exist_ok=True)


def test_CSR():
    setup()
    course = ghCourse(testCourse)

    templateRepo = course.assignmentsByName['asst1'].template_repo

    newAsstName = 'asst' + str(random.randint(2, 10000))

    course.assignmentsByName[newAsstName] = Assignment(newAsstName, templateRepo)
    course.save()

    OK: bool = create_student_repo(course, newAsstName, 'zeil')
    
    assert OK
    
    expectedRepoName = f"Fall26-test/{newAsstName}--szeil"
    
    
    course2 = ghCourse(testCourse)
    
    recordedNewRepo = False
    for row in course2.repositories:
        if (row.assignment == newAsstName and
            row.student == 'zeil' and
            row.repo == expectedRepoName and
            row.created.year == dt.datetime.now().year):
            recordedNewRepo = True
    assert recordedNewRepo

    course.deleteRepository(newAsstName, 'zeil')