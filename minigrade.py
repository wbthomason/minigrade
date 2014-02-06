from flask import Flask, render_template, request, jsonify, Response, abort, session, stream_with_context, redirect
from ast import literal_eval
import subprocess
import re
import requests
import json
import shutil
import time
import os

minigrade = Flask(__name__)    
# Put your own secret key here. You can't have mine!
minigrade.secret_key = '!\xec\xa8\x88\xc9R\xf7i<wW\x9fzH\x81\xff\x11~aQn\x9f\xcf\x0b'
urlmatch = re.compile('(?:git@|git://|https://)(?P<url>[\w@-]+\.[a-zA-Z]+[:/](?P<user>[a-zA-Z][a-zA-Z0-9-]+)/(?P<repo>.+))')

def process_repo(repo):
    result = urlmatch.match(repo)
    if not result:
        return None

    giturl = "https://" + result.group('url')
    repository = result.group('repo')
    if repository[-4:] == ".git":
        repository = repository[:-4]
    return (giturl, repository, result.group('user'))

def sort_files_by_age(files):
    filedata = [(filename, os.lstat(filename).st_ctime) for filename in files]
    filedata = sorted(filedata, key = lambda x: x[1])
    filedata = [filetuple[0] for filetuple in filedata]
    filedata = filter(lambda x: not os.path.isdir(x), filedata)
    return filedata

def cap_logs():
    result_files = os.listdir('.')
    if len(result_files) > 10:
        filedata = sort_files_by_age(result_files)[:len(result_files) - 10]
        for f in filedata:
            os.remove(f)


def grade_stream(assignment, repo):
    if 'email' not in session:
        yield "data: inv: Please log in before running the autograder.\n\n"
        raise StopIteration
    build = None
    tests = []
    repo_name = "NotADirectory"
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
    try:
        os.chdir("results/{}".format(assignment))
        if not os.path.isdir(session['email']):
            os.mkdir(session['email'])
        os.chdir(session['email'])
        cap_logs()
        result_files  = sort_files_by_age(os.listdir('.'))
        result_files.reverse()
        for f in result_files:
            yield "data: nextpast\n\n"
            with open(f) as result:
                for line in result:
                    yield "data: past: {}\n\n".format(line)

        with open(str(time.time())+".result", 'w') as results:
            result = process_repo(repo)
            if not result:
                results.write("{} is not a valid git repository.\n".format(repo))
                yield "data: inv: {} is not a valid git repository.\n\n".format(repo)
                raise StopIteration

            repo_url, repo_name, repo_user = result
            try:
                git = subprocess.check_output("git clone {}".format(repo_url).split(" "), stderr = subprocess.STDOUT)
                yield "data: raw: {}\n\n".format(git)
            except:
                results.write("{} is not a valid git repository.\n".format(repo))
                yield "data: inv: Error: {} is not a valid repository\n\n".format(repo)
                raise StopIteration
            results.write("Using repository {}.\n".format(repo))
            os.chdir(repo_name)
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
                    results.write("Build success\n")
                    yield "data: tr: Pass 0\n\n"
                else:
                    results.write("Build failed\n")
                    yield "data: tr: Fail 0\n\n"
                    yield "data: inv: Build failed!\n\n"
                    raise StopIteration
            passed = 0
            failed = 0
            for idnum, test in enumerate(tests):
                success = re.compile(test['results'])
                result = None
                for command in test['cmd'].split(";"):
                    yield "data: raw: {}\n\n".format(command)
                    try:
                        result = subprocess.check_output(command, shell = True, stderr = subprocess.STDOUT)
                    except Exception as e:
                        print "Error running test: {}. Got {}".format(test['name'], e)
                        results.write("Error running test {}\n".format(test['name']))

                    if result:
                        for line in result.split('\n'):
                            yield "data: raw: {}\n\n".format(line)
                    else: 
                        results.write("Error running test {}\n".format(command))
                        yield "data: raw: Error running {}\n\n".format(command)

                if result and re.search(success, result):
                    results.write("Passed {}\n".format(test['name']))
                    passed += 1
                    yield "data: tr: Pass {}\n\n".format(idnum + 1)
                else:
                    results.write("Failed {}\n".format(test['name']))
                    failed += 1
                    yield "data: tr: Fail {}\n\n".format(idnum + 1)

            results.write("Total pass: {}\n".format(passed))
            results.write("Total fail: {}\n".format(failed))
    finally:
        if os.path.isdir(repo_name):
            shutil.rmtree(repo_name)
        os.chdir('/home/grader/minigrade')

    yield "data: done\n\n"

@minigrade.route('/')
def index():
    with open("grade.html") as sub_page:
        return '\n'.join(sub_page.readlines())

@minigrade.route('/grade/')
def grade():
    assignment = request.args.get("assign", "NoneSuch")
    repo = request.args.get("repo", "NoneSuch")
    return Response(stream_with_context(grade_stream(assignment, repo)), mimetype="text/event-stream")

@minigrade.route('/auth/login', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return session['email'] if 'email' in session else "null"
    # The request has to have an assertion for us to verify
    if 'assertion' not in request.form:
        abort(400)

    # Send the assertion to Mozilla's verifier service.
    data = {'assertion': request.form['assertion'], 'audience': 'http://128.143.136.170:9080'}
    resp = requests.post('https://verifier.login.persona.org/verify', data=data, verify=True)

    # Did the verifier respond?
    if resp.ok:
        # Parse the response
        verification_data = json.loads(resp.content)

        # Check if the assertion was valid
        if verification_data['status'] == 'okay':
            # Log the user in by setting a secure session cookie
            session.update({'email': verification_data['email']})
            return "Logged in as %s" % verification_data['email']

    # Oops, something failed. Abort.
    abort(500)
    
@minigrade.route('/auth/logout', methods=['POST'])
def logout():
    session.pop('email', None)
    return redirect('/')
    
#Only run in chroot jail.
if __name__ == '__main__':
    #minigrade.run(host='0.0.0.0', debug=False, threaded=True, port=9080)
    minigrade.run(debug=True, threaded=True, port=9080)
