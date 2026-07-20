#!/usr/bin/python3
#
import csv
import logging
import os
import random
from pathlib import Path
import pytest
import shutil

from ghCourse import Assignment, Student, ghCourse

testCourse = 'build/testCourse'  

def setup():
    if Path.is_dir(Path(testCourse)):
        shutil.rmtree(testCourse)
    Path(testCourse).mkdir(parents=True, exist_ok=True)
    shutil.copytree('tests/data/course1', testCourse, dirs_exist_ok=True)


def test_ghCourse_constructor():
    setup()
    
    course = ghCourse(testCourse)
    assert course.accessID != None and course.accessID != ''
    assert course.studentsByName['zeil'].github_name == 'szeil'
    assert course.assignmentsByName['asst1'].template_repo == 'Fall26-test/test1'
    # repositories order may vary; ensure at least one repo is for asst2
    assert any(r.assignment == 'asst2' for r in course.repositories)
    
def test_ghCourse_save():
    setup()

    course0 = ghCourse(testCourse)
    lab1 = Assignment('lab1', 'organization/repo')
    course0.assignmentsByName['lab1'] = lab1
    course0.studentsByName['jdoe'] = Student('jdoe', 'jdoe2026')
    course0.save()
    
    course = ghCourse(testCourse)
    assert course.accessID != None and course.accessID != ''
    assert course.studentsByName['zeil'].github_name == 'szeil'
    assert course.studentsByName['jdoe'].github_name == 'jdoe2026'
    assert course.assignmentsByName['lab1'].template_repo == 'organization/repo'

def test_createStudentRepo():
    
    if Path.is_dir(Path(testCourse)):
        shutil.rmtree(testCourse)
    Path(testCourse).mkdir(parents=True, exist_ok=True)
    shutil.copytree('tests/data/course1', testCourse, dirs_exist_ok=True)
    
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