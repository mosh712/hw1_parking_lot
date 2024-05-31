from flask import Flask
from endpoints.entry import handle_entry
from endpoints.exit import handle_exit
from database import create_tables
import logging

app = Flask(__name__)

@app.route('/entry', methods=['POST'])
def entry():
    return handle_entry()

@app.route('/exit', methods=['POST'])
def exit():
    return handle_exit()

if __name__ == '__main__':
    logging.basicConfig(filename='parking.log', level=logging.DEBUG)
    logging.info("Initate server, creating tables")
    create_tables()
    app.run(debug=True, host='0.0.0.0', port=5000)
