wls#Path: server.py
from flask import Flask, request
from langchain import ChatOpenAI
from email_generator import email_endpoint

app = Flask(__name__)

@app.route('/server.py', methods=['POST'])
def generate_email_endpoint():
    # Get request data
    data = request.get_json()

    print(data)
    return email_endpoint()

if __name__ == '__main__':
    app.run(debug=True)