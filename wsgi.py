from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from extract import lppmunila_year, gscholar_idauthor, sinta_univ, sinta_author, SintaAuthor
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
    uname = os.getenv("USERNAME_SINTA")
    pw = os.getenv("PASSWORD_SINTA")
    ids = os.getenv("ID_PROFILE_SINTA")
    # url = "https://sinta.kemdikbud.go.id"
    sinta_author_data = SintaAuthor(uname, pw, ids)
    # sinta_author_data.sinta_login()
    sinta_author_data.sinta_scopus()
    sinta_author_data.sinta_wos()
    print(sinta_author_data.transform_dataframe())
    return render_template('sinta_author.html')

@app.route('/sinta_author_base', methods=['POST', 'GET'])
def sinta_author_base():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        id_sinta = request.form['id_sinta']
        return redirect(url_for('sinta_author_extract', uname=username, pw=password, ids=id_sinta))
    else:
        return render_template('sinta.html')

@app.route('/sinta_author_extract/<uname>/<pw>/<ids>')
def sinta_author_extract(uname=None, pw=None, ids=None):
    print(uname)
    print(pw)
    print(ids)
    # total_data, df = sinta_author(uname, pw, ids)
    total_data, df = sinta_author()
    print(total_data)
    return send_file(
                BytesIO(df.to_csv(index=False, encoding='utf-8').encode()),
                as_attachment=True,
                download_name=f'data_crawling_sinta_author_{today}',
                mimetype='text/excel')

if __name__ == "__main__":
    app.run(debug=True)