from flask import Flask, render_template, request, jsonify, Response
from ast import literal_eval
import subprocess

minigrade = Flask(__name__)

def grade_stream(assignment):
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
        yield "data: done\n\n"
    except:
        print "No test file for '{}'".format(assignment)
        yield "data: inv\n\n"

@minigrade.route('/')
def index():
    with open("grade.html") as sub_page:
        return '\n'.join(sub_page.readlines())

@minigrade.route('/grade/')
def grade():
    assignment = request.args.get("assign", "NoneSuch")
    return Response(grade_stream(assignment), mimetype="text/event-stream")

#Only run in chroot jail.
if __name__ == '__main__':
    minigrade.run(debug=True, threaded=True, port=80)