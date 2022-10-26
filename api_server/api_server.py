from flask import Flask
import json

app = Flask('name')

@app.route('/')
def helloworld():
    return 'Hello world!'

if __name__ == '__main__':
    app.run()