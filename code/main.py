from flask import Flask, render_template
import pymongo


app = Flask(__name__)

mongo_client = pymongo.MongoClient("mongodb://admin:admin@mongodb:27017", connect=False)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)