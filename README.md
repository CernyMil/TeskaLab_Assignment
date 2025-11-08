Hello,
I am sending the task description:
Before you start, create a repository on github.com and respond to this email with a link to this repo. Track your work, as you continue solving the task. Do not be discouraged, if everything does not look as smooth as you would like, or if some components do not work yet, until you say you are finished, the repository is treated as work in progress.

Your task will be to parse the provided dataset. It is a list of lxc containers in a testing environment in JSON format, and the output should be (for each container) its: name, cpu and memory usage, created_at, status and all the IP addresses that are assigned to it. Date fields should be in UTC timestamp format.

You can use any python libraries you are comfortable with, but if you want to truly shine, use asynchronous code (where appropriate).

As a source, there is this email attachment, and as for the output, your code should be loading parsed data to a database of your choice (could be relational or document based, but no SQLite please).

Also keep in mind, how to deploy your script “in production” (ideal scenario would be to have all the components dockerized).

Once you have thoroughly read and understood what needs to be done, respond to this email with time estimate to complete this task. Do not get discouraged if you are unable to complete some parts of this task, try a different one and you might find, that the obstacle is no longer there.