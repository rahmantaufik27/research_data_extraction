from flask import Flask, render_template, request, url_for, flash, redirect
import uvicorn

app = Flask(__name__)


@app.route('/')
def main():
    return 'main'

@app.route('/search')
def search():
    return 'search'

@app.route('/update')
def update():
    return 'update'

@app.route('/select')
def update():
    return 'select'

app.route('/extract')
def update():
    return 'extract'

# if __name__ == "__main__":
#     uvicorn.run("serve:app", reload=True, host="0.0.0.0", port=8000)