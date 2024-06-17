from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from extract import lppmunila_year, gscholar_idauthor, sinta_univ, sinta_author, SintaExtract
from datetime import date
from io import BytesIO
import pandas as pd
import os
from dotenv import load_dotenv

app = Flask(__name__)
today = date.today()

@app.route('/')
def main():
    return render_template('index.html')

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

@app.route('/sinta_author2')
def sinta_author2():
    return render_template('sinta_author.html')

@app.route('/sinta_author_base', methods=['POST', 'GET'])
def sinta_author_base():
    if request.method == "POST":
        # GET DATA FROM THE FORM
        # username = request.form['username']
        # password = request.form['password']
        # id_sinta = request.form['id_sinta']
        uname = os.getenv("USERNAME_SINTA") # login manually using default uname, pw, ids 
        pw = os.getenv("PASSWORD_SINTA")
        ids = os.getenv("ID_PROFILE_SINTA")
        return redirect(url_for('sinta_author_extract', uname=uname, pw=pw, ids=ids))
    else:
        return render_template('index.html')

@app.route('/sinta_author_extract/<uname>/<pw>/<ids>')
def sinta_author_extract(uname=None, pw=None, ids=None):
    # EXTRACT DATA SINTA START FROM THE LOGIN
    sinta_author_data = SintaExtract(uname, pw, ids)
    # EXTRACT DATA PER SINTA TYPE
    total_data, df = sinta_author_data.sinta_author("scopus")
    print(total_data)

    # RETURN AS A FILE
    return send_file(
                BytesIO(df.to_csv(index=False, encoding='utf-8').encode()),
                as_attachment=True,
                download_name=f'data_crawling_sinta_author_{today}',
                mimetype='text/csv')

if __name__ == "__main__":
    app.run(debug=True)