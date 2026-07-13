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
    
    course = ghCourse('tests/data/course1/')
    assert course.accessID != None and course.accessID != ''
    assert course.student2GHLogin['zeil'] == 'sjzeil'
    assert course.ghLogin2Student['sjzeil'] == 'zeil'
    assert course.asst2Template['asst1'] == 'Fall26-test/test1'
    
