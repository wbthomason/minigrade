from flask import Flask, render_template, request, jsonify
minigrade = Flask(__name__)

@minigrade.route('/')
def index():
    with open("grade.html") as sub_page:
        return '\n'.join(sub_page.readlines())


if __name__ == '__main__':
    minigrade.run(debug=True)