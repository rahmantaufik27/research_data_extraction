from project import wsgi

def run_flask_app():
    wsgi.run(debug=True)

if __name__ == '__main__':
    # Run the Flask app in a separate thread
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.start()

    # You can add other logic here that runs in parallel with the Flask app
    print("Flask app is running in a separate thread.")


