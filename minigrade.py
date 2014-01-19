from flask import Flask, render_template, request, jsonify, Response
from ast import literal_eval
import subprocess

minigrade = Flask(__name__)

def grade_stream(assignment):
    build = None
    tests = []
    try:
        with open("tests/PS1.test".format(assignment)) as testfile:
            for idnum, testcase in enumerate(testfile):
                test = literal_eval(' '.join(testcase.split(' ')[1:]))
                if testcase.split(' ')[0] == "build":
                    build = test
                else:
                    tests.append(test)

                yield "data: tn: {} {}\n\n".format(test['name'], idnum)
        
        yield "data: tr: Pass 0\n\n"
        yield "data: tr: Fail 3\n\n"
        yield "data: raw: Raw Output\n\
data: on multiple lines!! \n\n"
        yield "data: done\n\n"
    except:
        print "No test file for '{}'".format(assignment)
        yield "data: No valid test file exists.\n\n"
        yield "data: done\n\n"

@minigrade.route('/')
def index():
    with open("grade.html") as sub_page:
        return '\n'.join(sub_page.readlines())

@minigrade.route('/grade/')
def grade():
    assignment = request.args.get("assign", "NoneSuch")
    return Response(grade_stream(assignment), mimetype="text/event-stream")

if __name__ == '__main__':
    minigrade.run(debug=True, threaded=True, port=80)