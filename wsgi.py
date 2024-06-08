from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from extract import lppmunila_year, gscholar_idauthor, sinta_univ, sinta_author
from datetime import date
from io import BytesIO
import pandas as pd

app = Flask(__name__)
today = date.today()

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
    total_data, df = sinta_author()
    print(total_data)
    return send_file(
                BytesIO(df.to_csv(index=False, encoding='utf-8').encode()),
                as_attachment=True,
                download_name=f'data_crawling_sinta_author_{today}',
                mimetype='text/excel')

if __name__ == "__main__":
    app.run(debug=True)