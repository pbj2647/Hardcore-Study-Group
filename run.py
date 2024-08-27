from flask import Flask, render_template
run = Flask(__name__)

if __name__ == '__main__':
    run.run(debug=True)