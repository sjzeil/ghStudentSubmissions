#!/usr/bin/python3
#
import csv
import logging
import os
import random
from pathlib import Path
import pytest
import shutil

from create_student_repo import readAccessID, createStudentRepo

testCourse = 'build/testCourse'  

def setup():
    if Path.is_dir(testCourse):
        shutil.rmtree(testCourse)
    Path(testCourse).mkdir(parents=True, exist_ok=True)
    shutil.copytree('tests/data/course1', testCourse, dirs_exist_ok=True)


def test_CSR():
    setup()
    accessId = readAccessID(str(Path.home / '.github'))
    msg = createStudentRepo(accessId, testCourse, 'asst1', 'zeil')
    
    assert not ('Error' in msg)
    expectedRepoName = 'Fall26-test/test1--szeil'
    assert expectedRepoName in msg

    with open(f"{testCourse}/repositories.csv", mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)

        recordedNewRepo = False
        for row in reader:
            print(row)
            if (row['Assignment'] == 'asst1' and
                row['CS Login'] == 'zeil' and
                row['Repository'] == expectedRepoName and
                row['Created'].startswith('202')):
                recordedNewRepo = True
        assert recordedNewRepo

