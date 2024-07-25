from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from extract import lppmunila_year, gscholar_idauthor, SintaExtract
from datetime import date
from io import BytesIO
import pandas as pd
import os
from dotenv import load_dotenv
import xlsxwriter

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

@app.route('/sinta_author2')
def sinta_author2():
    return render_template('sinta_author.html')

@app.route('/try_load')
def try_load():
    return render_template('loading-test.html')

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

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return send_file(output, download_name=f"data_crawling_sinta_author_pub_{today}.xlsx", as_attachment=True)

@app.route('/sinta_author_pub_extract')
def sinta_author_pub_extract():
    uname = os.getenv("USERNAME_SINTA") # login manually using default uname, pw, ids 
    pw = os.getenv("PASSWORD_SINTA")
    ids = ['6680581', '6680844', '6023686', '5980587', '6657292', '6680511', '6729923', '6155915', '6021756', '6156734', '6808429', '6023917', '6156872', '5980605', '6140651', '6680562', '6081289', '6156743', '6156833', '6125066', '6717407', '6704618', '6705331', '6813851', '6808368', '6800649', '6842107', '6158846']
    # ids = ['6680581', '6680844']
    pub_type = ['scopus', 'wos', 'garuda', 'googlescholar']
    df = pd.DataFrame()
    for i in ids:
        print(i)
        sinta_author_data = SintaExtract(uname, pw, i)
        for t in pub_type:
            df = sinta_author_data.sinta_author_pub(t)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return send_file(output, download_name=f"data_crawling_sinta_author_pub_{today}.xlsx", as_attachment=True)
    
@app.route('/sinta_author_research_extract')
def sinta_author_research_extract():
    uname = os.getenv("USERNAME_SINTA") # login manually using default uname, pw, ids 
    pw = os.getenv("PASSWORD_SINTA")
    ids = ['6680581', '6680844', '6023686', '5980587', '6657292', '6680511', '6729923', '6155915', '6021756', '6156734', '6808429', '6023917', '6156872', '5980605', '6140651', '6680562', '6081289', '6156743', '6156833', '6125066', '6717407', '6704618', '6705331', '6813851', '6808368', '6800649', '6842107', '6158846']
    # ids = ['5980605', '6680581', '6680844']
    # pub_type = ['researches', 'services', 'iprs', 'books']
    pub_type = ['researches', 'services']
    df = pd.DataFrame()
    for i in ids:
        print(i)
        sinta_author_data = SintaExtract(uname, pw, i)
        for t in pub_type:
            df = sinta_author_data.sinta_author_research(t)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Sheet1")
    output.seek(0)
    return send_file(output, download_name=f"data_crawling_sinta_author_research_{today}.xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)