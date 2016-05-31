from flask import Flask

from app import app

print('Running Server')
if __name__ == '__main__':
    app.run(debug = True)
print('Stopping Server')
