# Setup and Operations

This document explains how to set up a basic replacement for GitHub classroom for a course each semester.

This will allow

* distribution of assignments via GitHub, 
* collection of students' submissions via git & GitHub

It does not include an auto-grading facility, but should be compatible with any such facility you like.



## Semester Setup


### Create a GitHub organization for the course & semester 

All repositories for the course will be kept in a Github "organization".  You, as the organization admin, will create a "template" repository with the starting files for each assignment in this organization. Students will then request and be granted a repository with a copy of the starting files.   Students will have access to these repositories, you they will be owned by the organization and, therefore, by you.

After sufficient time has elapsed after your course has completed, you can "clean up" by having GitHub delete the organization, which will delete the repositories in that organization as well.

To create an organization:

1. Log into GitHub.
2. Click on your icon/picture in the upper right and select "Organizations".
3. Use the "New Organization" button to create an organization. The "free" level of organization should suffice.   Name this for your course and semester, e.g., "ODU_CS361_Fall26".

### Clone this repo

Clone this repository into a convenient location. You may share this clone among multiple courses and semesters.

### Create the course information area

The course information area is a directory containing, at a minimum:  

* an access code allowing automated access to your new Github organization, 
* a list of students identified by your local identifiers and the GitHub account names for those students (these will be supplied by the students).
* a list of assignments and the names of the Github template repos containing the starting files for each assignment
* a list of repos that have been created for your students

This area may also wind up containing clones of the student repositories.


1. Create a directory you want to use for this purpose. This should be accessible from, but not directly served by your web server.
2. Copy the `*.py` files from `src/` into this directory.
2. In that directory, create a file named `.github` with your favorite editor.
3. In a web browser, visit GitHub.  Click on your icon/picture in the upper right.

    Click Settings, then Developer Settings

    Expand the Personal access tokens menu and click `Fine-grained tokens`.

    Click 'Generate new token' and follow the instructions. 
    
    * For "Resource owner", select the Organization you created earlier.
    * For "Repository Access", "All repositories"
    * For "Permissions", add the following permissions:
        * Administration --- Set Access to "Read and Write"
        * Contents (automatically adds Metadata) --- Set Access to "Read-only"


    Click 'Generate token`.     _Immediately_ copy and paste the token into the `.github` file you created in step 2. Save that.

### Set up the web pages

1. Copy the contents of the `src/php` directory to an appropriate directory served by your web server.   This directory should be password-protected to restrict access to your students.
2. Edit the `configuration.php` file. The most important parts here are

    * `courseInformation`, should contain the path to your course information directory set up in the previous section.
    * `ghStudentSubmissions`, should contain the path to your clone of this repo.



## Assignment Setup

1. In your course assignment page, create a link to the `getStartingCode.php` page.
2. In GitHub, visit your course organization. 
    1. Go to Repositories
    2. Use the New repository" button to create a new repo for the starting code. 
    3. On the repo's page, click `Settings`, then place a checkmark in the "template repository" box.
    4. Add the starting files to the repository.
2. In the course information area, add your assignment to `templates.csv`.  The format is: _your_assignment_name,template_repo_name_.  For example, if your "Assignment 1" has its template repo in `ODU_CS361_Fall26/Asst1", add a line:

         Assignment 1,ODU_CS361_Fall26/Asst1

Students who visit the `getStartingCode.php` will now see "Assignment 1" among the choices of possible assignments. 

* If they chose that and do not have a repo for that assignment yet, one will be created and they will be told it's URL.   
* If they chose that and already have a repo for that assignment, they will be reminded of it's URL.



## Coming Eventually

1. The ability to specify whether students have admin rights on their repositories.
2. Support for team projects



