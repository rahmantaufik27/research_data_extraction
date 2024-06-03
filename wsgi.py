from flask import Flask, render_template, request, url_for, flash, redirect
from extract import lppmunila_year, gscholar_idauthor, sinta_univ, sinta_author
import uvicorn

app = Flask(__name__)

@app.route('/')
def main():
    return 'hello mother father'

@app.route('/lppmunila_year')
def extract_lppmunila_year():
    lppmunila_year()
    return 'lppmunila_year'

@app.route('/gscholar_idauthor')
def extract_gscholar_idauthor():
    gscholar_idauthor()
    return 'gscholar_idauthor'

@app.route('/sinta_univ')
def extract_sinta_univ():
    sinta_univ()
    return 'Done'

@app.route('/sinta_author')
def extract_sinta_author():
    sinta_author()
    return 'sinta author done'

if __name__ == "__main__":
    app.run(debug=True)
#     uvicorn.run("wsgi:app", reload=True, host="localhost", port=5050)