#!/usr/bin/python3
#
import csv
import logging
import os
import random
from pathlib import Path
import pytest
import shutil

from ghCourse import ghCourse

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
    assert course.student2GHLogin['zeil'] == 'szeil'
    assert course.ghLogin2Student['szeil'] == 'zeil'
    assert course.asst2Template['asst1'] == 'Fall26-test/test1'
    assert course.repositories[0].assignmentName == 'asst2'
    
def test_ghCourse_save():
    setup()

    course0 = ghCourse(testCourse)
    course0.asst2Template['lab1'] = 'organization/repo'
    course0.student2GHLogin['jdoe'] = 'jdoe2026'
    course0.save()
    
    course = ghCourse(testCourse)
    assert course.accessID != None and course.accessID != ''
    assert course.student2GHLogin['zeil'] == 'szeil'
    assert course.student2GHLogin['jdoe'] == 'jdoe2026'
    assert course.ghLogin2Student['szeil'] == 'zeil'
    assert course.asst2Template['lab1'] == 'organization/repo'
