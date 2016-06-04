from flask import Flask

from app import app

print('Running Server')
if __name__ == '__main__':
    app.run(debug = True, host= '0.0.0.0')
print('Stopping Server')
