
from flask import Flask
from evelyn import create_app

print('Running Server')
app = create_app('../application.cfg')
if __name__ == '__main__':
    app.run(debug = True, host= '0.0.0.0')
print('Stopping Server')
