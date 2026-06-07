from flask import Flask

app = Flask(__name__)

@app.route('/print', methods=['POST'])
def print_to_terminal():
    print("Hello from Python! This is printed in the terminal.")
    return 'Printed', 200

if __name__ == '__main__':
    app.run(debug=True)
