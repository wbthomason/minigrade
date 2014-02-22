from flask import Flask, render_template, request, jsonify, Response, abort, session, stream_with_context, redirect, g
from ast import literal_eval
import subprocess
import re
import requests
import json
import shutil
import time
import os
import sqlite3


minigrade = Flask(__name__)    
# Put your own secret key here. You can't have mine!
minigrade.secret_key = '!\xec\xa8\x88\xc9R\xf7i<wW\x9fzH\x81\xff\x11~aQn\x9f\xcf\x0b'
urlmatch = re.compile('(?:git@|git://|https://)(?P<url>[\w@-]+\.[a-zA-Z]+[:/](?P<user>[a-zA-Z][a-zA-Z0-9-]+)/(?P<repo>.+))')

PORT_NUMBER = 9080
SERVER_IP = 'http://128.143.136.170'

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
    cwd = os.getcwd()
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
            if os.path.isdir(repo_name):
                shutil.rmtree(repo_name)
            try:
                git = subprocess.check_output("git clone {}".format(repo_url).split(" "), stderr = subprocess.STDOUT)
                yield "data: raw: {}\n\n".format(git)
            except Exception as e:
                results.write("{} is not a valid repository, because we got {}\n".format(repo,e))
                yield "data: inv: Error: {} is not a valid repository, because we got {}\n\n".format(repo,e)
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
	    counter = 0
            for idnum, test in enumerate(tests):
		counter += 1
                yield "data: raw: {}\n\n".format(test["cmd"])
		success = re.compile(test['results'])
		f = open("test_file{}".format(counter), 'w')
		temp=""
		for token in test['cmd'].split(';'):
			temp = temp + './gash -c "{}"\n'.format(token)
		#print "temp={}".format(temp.rstrip())
		f.write(temp.rstrip())
		f.close()
		cwd = os.getcwd()
		#print "cwd={}".format(cwd)
		command = "/home/grader/minigrade/dockerscript.sh {} {} test_file{} output_file{}".format(cwd, cwd, counter, counter)
		#print "command={}".format(command)		
		returncode = subprocess.call(command, shell = True, stderr = subprocess.STDOUT)
		result =""
		r = open('output_file{}'.format(counter), 'r')
		result = ''.join(r.readlines()).rstrip()
		r.close()
		#print "result from output_file{}={}".format(counter, result)
		#print "done printing result"
		print "{}: test {}".format(session['email'], counter)
		#print "returncode={}".format(returncode)
		for line in result.split('\n'):
		    yield "data: raw: {}\n\n".format(line)
                if (returncode == 0) and re.search(success, result):
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
        os.chdir(cwd)

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
    data = {'assertion': request.form['assertion'], 'audience': SERVER_IP + ':'+ str(PORT_NUMBER)}
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


# Server-side database methods
##########


@minigrade.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        if error:
            print("There was an error closing the database")


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect('database.db')
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def init_db():
    """Creates the database tables."""
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()


def query_db(query, args=(), one=False):
    """Returns a query to the database as a list"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    get_db().commit()
    return (rv[0] if rv else None) if one else rv

# Leaderboard functions
#################

import random
@minigrade.route('/leaderboard.html')
def leaderboard():
    update_leaderboard(5)
    users = ['abc', 'zl4ry', 'asdf', 'jkl;', 'WIL']
    update_top_runs(random.choice(users), random.random(), random.random())
    with open("leaderboard.html") as sub_page:
        return '\n'.join(sub_page.readlines())

def update_top_runs(user, duration, response):
    print(user, duration, response)
    q = query_db("SELECT * FROM topruns WHERE username=?", [user], one=True)
    print q
    if q is None:
	query_db("INSERT INTO topruns VALUES (?, ?, ?)", [user, str(duration), str(response)])
    else:
	query_db("UPDATE topruns SET duration=?, response=? WHERE username=?", [str(duration), str(response), user])

def get_top_runs(num):
    ''' Returns the top num runs in a list of 3xnum elements:
	the first is best duration/response time,
	the second is best duration, third is response time'''
    runs = query_db("SELECT * FROM topruns")
    data = [[],[],[]]
    runs.sort(key=heuristic)
    data[0] = runs[:num]
    runs.sort(key=lambda x: float(x[1]))
    data[1] = runs[:num]
    runs.sort(key=lambda x: float(x[2]))
    data[2] = runs[:num]
    return data

def heuristic(run):
    '''returns a function of a weighing bewteen duration and response time'''
    return float(run[1]) * float(run[2])

def update_leaderboard(num):
    '''Updates the leaderboard for webpages to see'''
    head = "<h2>Leaderboard</h2>"
    tbl_template=lambda x: '''
<h3>%s</h3>
<table id="leaderboard-dr" style='width:100%%%%;border-spacing:10px'>
    <tr><th style="text-align:left">ID</th>
	<th style="text-align:left">Duration Time</th>
	<th style="text-align:left">Response Time</th>
    </tr>
    %%s
</table>
'''%x
    titles = ["Best duration/response time", "Best duration", "Best Response Time"]

    data = get_top_runs(num)
    fin = ""
    for i, title in enumerate(titles):
	tmp = tbl_template(title)
	row = ""
	for tup in data[i]:
	    # should be (username, duration, response time)
	    row += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(*tup)
	fin += tmp%row
    open("leaderboard.html", 'w').write(fin)
    

#Only run in chroot jail.
if __name__ == '__main__':
    minigrade.run(host='0.0.0.0', debug=False, threaded=True, port=PORT_NUMBER)
    #minigrade.run(debug=True, threaded=True, port=9080)
