#!/usr/bin/python3
#
import csv
import logging
import os
import random
from pathlib import Path
import pytest
import shutil

from ghCourse import ghCourse, Assignment

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

    msg = course.createStudentRepo(newAsstName, 'zeil')
    
    assert not ('Error' in msg)
    expectedRepoName = f"Fall26-test/{newAsstName}--szeil"
    assert expectedRepoName in msg

    course.save()

    with open(f"{testCourse}/repositories.csv", mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        recordedNewRepo = False
        for row in reader:
            print(row)
            if (row['assignment'] == newAsstName and
                row['student'] == 'zeil' and
                row['repo'] == expectedRepoName and
                row['created'].startswith('202')):
                recordedNewRepo = True
        assert recordedNewRepo

    course.deleteRepository(newAsstName, 'zeil')