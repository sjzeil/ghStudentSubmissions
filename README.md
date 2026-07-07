# ghStudentSubmissions
A set of scripts to manage student assignments via GitHub.

Specifically:

* Allow distribution of starting code as a copy of template repo in a GitHub organization.  This organization can represent one or multiple courses, each with multiple assignments.
* Students are not members of that organization, but are added as collaborators to their new assignment repository.
* Templates can provide GitHub actions to trigger notifications of pushes or automatic grading.   Because all student repos belong to the same organization, a custom action-runner can be used.
* Automatic grading is not itself part of this project, as richer options can be found as separate projects (including my own [code-grader](https://github.com/sjzeil/code-grader)).


