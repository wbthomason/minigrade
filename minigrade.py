from flask import Flask, render_template, request, jsonify, Response
from ast import literal_eval
import subprocess
import re

minigrade = Flask(__name__)    

def process_repo(repo):
    if len(repo) < 8:
        return ("BadRepo", "NoName")
    urlstart = 6 if repo[:3] == "git" else 8
    try:
        name = repo[urlstart:].split('/')[2].split('.')[0]
    except IndexError:
        return ("BadRepoUrlGiven", "NoName")
    giturl = "git://" + repo[urlstart:]
    return (giturl, name)

def grade_stream(assignment, repo):
    build = None
    tests = []
    try:
        with open("tests/{}.test".format(assignment)) as testfile:
            for idnum, testcase in enumerate(testfile):
                test = literal_eval(' '.join(testcase.split(' ')[1:]))
                if testcase.split(' ')[0] == "build":
                    build = test
                else:
                    tests.append(test)

                yield "data: tn: {} {}\n\n".format(test['name'], idnum)
    except:
        print "No test file for '{}'".format(assignment)
        yield "data: inv: Error: No valid test file for {}\n\n".format(assignment)
        raise StopIteration
    git_repo, repo_name = process_repo(repo)
    try:
        git = subprocess.check_output("git clone {}".format(git_repo).split(" "), stderr = subprocess.STDOUT)
        yield "data: raw: {}\n\n".format(git)
    except:
        yield "data: inv: Error: {} is not a valid repository\n\n".format(repo)
        raise StopIteration
    if build:
        success = re.compile(build['results'])
        commands = build['cmd'].split(";")
        for command in commands:
            yield "data: raw: {}\n\n".format(command)
            result = None
            try:
                result = subprocess.check_output(command, shell = True, stderr = subprocess.STDOUT)
            except:
                print "Error building"

            if result:
                for line in result.split('\n'):
                    yield "data: raw: {}\n\n".format(line)
            else: 
                yield "data: raw: Error running {}\n\n".format(command)

        if result and re.search(success, result):
            yield "data: tr: Pass 0\n\n"
        else:
            yield "data: tr: Fail 0\n\n"
            yield "data: inv: Build failed!\n\n"
            raise StopIteration

    for idnum, test in enumerate(tests):
        success = re.compile(test['results'])
        result = None
        for command in test['cmd'].split(";"):
            yield "data: raw: {}\n\n".format(command)
            try:
                result = subprocess.check_output(command, shell = True, stderr = subprocess.STDOUT)
            except:
                print "Error running test: {}".format(test['name'])

            if result:
                for line in result.split('\n'):
                    yield "data: raw: {}\n\n".format(line)
            else: 
                yield "data: raw: Error running {}\n\n".format(command)

        if result and re.search(success, result):
            yield "data: tr: Pass {}\n\n".format(idnum + 1)
        else:
            yield "data: tr: Fail {}\n\n".format(idnum + 1)

    yield "data: done\n\n"

@minigrade.route('/')
def index():
    with open("grade.html") as sub_page:
        return '\n'.join(sub_page.readlines())

@minigrade.route('/grade/')
def grade():
    assignment = request.args.get("assign", "NoneSuch")
    repo = request.args.get("repo", "NoneSuch")
    return Response(grade_stream(assignment, repo), mimetype="text/event-stream")

#Only run in chroot jail.
if __name__ == '__main__':
    minigrade.run(debug=True, threaded=True, port=9080)