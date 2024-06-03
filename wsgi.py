from flask import Flask, render_template, request, url_for, flash, redirect
from extract import lppmunila_year, gscholar_idauthor, sinta_univ
import uvicorn

app = Flask(__name__)

@app.route('/')
def main():
    return 'hello mother father'

@app.route('/lppmunila_year')
def search():
    return 'lppmunila_year'

@app.route('/gscholar_idauthor')
def update():
    gscholar_idauthor()
    return 'gscholar_idauthor'

if __name__ == "__main__":
    app.run(debug=True)
#     uvicorn.run("wsgi:app", reload=True, host="localhost", port=5050)