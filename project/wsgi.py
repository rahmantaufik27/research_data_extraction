from flask import Flask, render_template, request, jsonify, url_for, flash, redirect, send_file
from extract import lppmunila_year, gscholar_idauthor, SintaExtract
from datetime import date
from io import BytesIO
import pandas as pd
import os
from dotenv import load_dotenv
import xlsxwriter
import ast

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

@app.route('/sinta_author_display')
def sinta_author_display():
    return render_template('sinta_author.html')

@app.route('/try_load')
def try_load():
    return render_template('loading-test.html')

@app.route('/sinta_author_base', methods=['POST', 'GET'])
def sinta_author_base():
    if request.method == "POST":
        # GET DATA FROM THE FORM
        username = request.form['username']
        password = request.form['password']
        id_sinta = request.form['id_sinta']
        entity = request.form['entity']
        category = request.form.getlist('category')
        ids = [item.strip() for item in id_sinta.split(',')]
        print(username, password, ids, entity, category)
        
        # df_pub_s = pd.DataFrame()
        # df_pub_g = pd.DataFrame()
        # df_pub_w = pd.DataFrame()
        # df_pub_gs = pd.DataFrame()
        # df_r = pd.DataFrame()
        # df_s = pd.DataFrame()
        # df_ip = pd.DataFrame()
        # df_b = pd.DataFrame()

        # df = pd.DataFrame()
        # output = BytesIO()
        # with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        #     for i in ids:
        #         print(i)
        #         sinta_author_data = SintaExtract(username, password, i)
        #         for cat in category:
        #             df = sinta_author_data.sinta_author(cat, entity, cat)
        #             df.to_excel(writer, index=False, sheet_name=cat)
        # output.seek(0)
    
        # return send_file(output, download_name=f"data_crawling_sinta_author_{today}.xlsx", as_attachment=True)

        output = BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            sinta_author_data = SintaExtract(username, password, None)
            for cat in category:
                df_list = []
                for i in ids:
                    print(i)
                    sinta_author_data.ids = i  # Update the ID within the same object
                    if cat == "scopus":
                        df_list.append(sinta_author_data.sinta_author_pub(cat, entity))
                    elif cat == "garuda":
                        df_list.append(sinta_author_data.sinta_author_pub(cat, entity))
                    elif cat == "wos":
                        df_list.append(sinta_author_data.sinta_author_pub(cat, entity))
                    elif cat == "googlescholar":
                        df_list.append(sinta_author_data.sinta_author_pub(cat, entity))
                    elif cat == "researches":
                        df_list.append(sinta_author_data.sinta_author_research(cat, entity))
                    elif cat == "services":
                        df_list.append(sinta_author_data.sinta_author_research(cat, entity))
                    elif cat == "iprs":
                        df_list.append(sinta_author_data.sinta_author_ipr(cat, entity))
                    elif cat == "books":
                        df_list.append(sinta_author_data.sinta_author_book(cat, entity))
                
                # Concatenate all DataFrames for the current category
                if df_list:
                    df_combined = pd.concat(df_list, ignore_index=True)
                    sheet_name = {
                        "scopus": "Scopus Publications",
                        "garuda": "Garuda Publications",
                        "wos": "WoS Publications",
                        "googlescholar": "Google Scholar Publications",
                        "researches": "Researchs",
                        "services": "Services",
                        "iprs": "IPRs",
                        "books": "Books"
                    }[cat]
                    df_combined.to_excel(writer, index=False, sheet_name=sheet_name)
        output.seek(0)
        return send_file(output, download_name=f"data_crawling_sinta_{today}.xlsx", as_attachment=True)
    else:
        return render_template('index.html')

# @app.route('/sinta_author_pub_extract')
# def sinta_author_pub_extract():
#     uname = os.getenv("USERNAME_SINTA") # login manually using default uname, pw, ids 
#     pw = os.getenv("PASSWORD_SINTA")
#     ids = ['6680581', '6680844', '6023686', '5980587', '6657292', '6680511', '6729923', '6155915', '6021756', '6156734', '6808429', '6023917', '6156872', '5980605', '6140651', '6680562', '6081289', '6156743', '6156833', '6125066', '6717407', '6704618', '6705331', '6813851', '6808368', '6800649', '6842107', '6158846']
#     # ids = ['6680581', '6680844', '6085792']
#     pub_type = ['scopus', 'wos', 'garuda', 'googlescholar']
#     df = pd.DataFrame()
#     for i in ids:
#         print(i)
#         sinta_author_data = SintaExtract(uname, pw, i)
#         for t in pub_type:
#             df = sinta_author_data.sinta_author_pub(t)
    
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         df.to_excel(writer, index=False, sheet_name="Sheet1")
#     output.seek(0)
#     return send_file(output, download_name=f"data_crawling_sinta_author_pub_{today}.xlsx", as_attachment=True)
    
# @app.route('/sinta_author_research_extract')
# def sinta_author_research_extract():
#     uname = os.getenv("USERNAME_SINTA") # login manually using default uname, pw, ids 
#     pw = os.getenv("PASSWORD_SINTA")
#     ids = ['6680581', '6680844', '6023686', '5980587', '6657292', '6680511', '6729923', '6155915', '6021756', '6156734', '6808429', '6023917', '6156872', '5980605', '6140651', '6680562', '6081289', '6156743', '6156833', '6125066', '6717407', '6704618', '6705331', '6813851', '6808368', '6800649', '6842107', '6158846', '6085792']
#     # ids = ['5980605', '6680581', '6680844']
#     pub_type = ['researches', 'services']
#     df = pd.DataFrame()
#     for i in ids:
#         print(i)
#         sinta_author_data = SintaExtract(uname, pw, i)
#         for t in pub_type:
#             df = sinta_author_data.sinta_author_research(t)
    
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         df.to_excel(writer, index=False, sheet_name="Sheet1")
#     output.seek(0)
#     return send_file(output, download_name=f"data_crawling_sinta_author_research_{today}.xlsx", as_attachment=True)

# @app.route('/sinta_author_ipr_extract')
# def sinta_author_ipr_extract():
#     uname = os.getenv("USERNAME_SINTA") # login manually using default uname, pw, ids 
#     pw = os.getenv("PASSWORD_SINTA")
#     # ids = ['6680581', '6680844', '6023686', '5980587', '6657292', '6680511', '6729923', '6155915', '6021756', '6156734', '6808429', '6023917', '6156872', '5980605', '6140651', '6680562', '6081289', '6156743', '6156833', '6125066', '6717407', '6704618', '6705331', '6813851', '6808368', '6800649', '6842107', '6158846', '6085792']
#     ids = ['5980605']
#     pub_type = ['iprs']
#     df = pd.DataFrame()
#     for i in ids:
#         print(i)
#         sinta_author_data = SintaExtract(uname, pw, i)
#         for t in pub_type:
#             df = sinta_author_data.sinta_author_ipr(t)
    
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         df.to_excel(writer, index=False, sheet_name="Sheet1")
#     output.seek(0)
#     return send_file(output, download_name=f"data_crawling_sinta_author_ipr_{today}.xlsx", as_attachment=True)

# @app.route('/sinta_author_book_extract')
# def sinta_author_book_extract():
#     uname = os.getenv("USERNAME_SINTA") # login manually using default uname, pw, ids 
#     pw = os.getenv("PASSWORD_SINTA")
#     # ids = ['6680581', '6680844', '6023686', '5980587', '6657292', '6680511', '6729923', '6155915', '6021756', '6156734', '6808429', '6023917', '6156872', '5980605', '6140651', '6680562', '6081289', '6156743', '6156833', '6125066', '6717407', '6704618', '6705331', '6813851', '6808368', '6800649', '6842107', '6158846', '6085792']
#     ids = ['5980605']
#     pub_type = ['books']
#     df = pd.DataFrame()
#     for i in ids:
#         print(i)
#         sinta_author_data = SintaExtract(uname, pw, i)
#         for t in pub_type:
#             df = sinta_author_data.sinta_author_book(t)
    
#     output = BytesIO()
#     with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
#         df.to_excel(writer, index=False, sheet_name="Sheet1")
#     output.seek(0)
#     return send_file(output, download_name=f"data_crawling_sinta_author_book_{today}.xlsx", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)