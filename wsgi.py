from flask import Flask, render_template, request, url_for, flash, redirect
from extract import lppmunila_year, gscholar_idauthor
import uvicorn

app = Flask(__name__)

@app.route('/')
def main():
    return 'hellomotherfather'

@app.route('/lppmunila_year')
def search():
    return 'lppmunila_year'

@app.route('/gscholar_idauthor')
def update():
    gscholar_idauthor
    return 'gscholar_idauthor'

# if __name__ == "__main__":
#     uvicorn.run("wsgi:app", reload=True, host="0.0.0.0", port=5000)