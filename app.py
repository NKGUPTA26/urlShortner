from hashids import Hashids
from flask import Flask, request, flash, redirect, url_for,Response,jsonify
import json
from datetime import datetime
from models.Url import Url,Clicks
from database import db
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
load_dotenv()
app = Flask(__name__)

app.config['SECRET_KEY'] = str(os.environ.get("SECRET_KEY"))

hashids = Hashids(min_length=4, salt=app.config['SECRET_KEY'])

def toJSON(data):
    return json.dumps(data, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)

def responseSender(response):
    response = Response(json.dumps(response))
    response.headers['Content-type'] = 'application/json'
    return response

@app.route('/', methods=['POST'])
def index():

    if request.method == 'POST':
        url = request.form['url']
        if not url:
            response = {"success": False,"message":"URL is not provided"}
            return responseSender(response), 400
        response = requests.get(url)
        url_data = Url(original_url=url)
        db.session.add(url_data)
        db.session.commit()
        click = Clicks(url_id=url_data.id, url_click_at_time=1)
        db.session.add(click)
        url_id = url_data.id
        hashid = hashids.encode(url_id)
        short_url = request.host_url + hashid
        url_details = Url.query.filter_by(id=url_id).first()
        url_details.short_url = short_url
        db.session.commit()
        response = {"success": True, "short_url":short_url}
        return responseSender(response)

@app.route('/<id>',methods = ["GET"])
def url_redirect(id):
    try:
        original_id = hashids.decode(id)
        meta = request.args.get("meta")
        if not meta:
            if original_id :
                original_id = original_id[0]
                url = Url.query.filter_by(id=original_id).first()
                original_url = url.original_url
                clicks = url.total_clicks
                updateDetails = Url.query.filter_by(id=original_id).first()
                updateDetails.total_clicks += 1
                click_data = Clicks(url_id = original_id , url_click_at_time = 1)
                db.session.add(click_data)
                db.session.commit()
                return redirect(original_url),302
            else:
                response = {"message":"shotrned endpoint not added","status":False}
                return responseSender(response),422
        else:
            if original_id :
                original_id = original_id[0]
                url = Url.query.filter_by(id=original_id).first()
                timeCreated = url.datetime
                timenow = datetime.now()
                h, s = divmod((timenow - timeCreated).total_seconds(), 3600)
                if int(h) <= 0:
                    hourly_hit_rate = url.total_clicks
                else:
                    hourly_hit_rate = url.total_clicks // h
                response = {"original_url":url.original_url,"short_url":url.short_url,"hourly_hit_rate":hourly_hit_rate,"total_hit":url.total_clicks}
                return responseSender(response)
            else:
                response = {"message":"shotrned endpoint not added","status":False}
                return responseSender(response) ,422
    except:
        response = {"message": "something went wrong", "status": False}
        return responseSender(response),500


@app.route('/search/<title>', methods=["GET"])
def search_title_page(title):
    try:
        if title:
            data = Url.query.filter(Url.original_url.contains(title)).all()
            store = {}
            store["original_url"] = []
            store["short_url"] = []
            for d in data:
                store["original_url"].append(d.original_url)
                store["short_url"].append(d.short_url)
            if len(data) == 0:
                return responseSender({"message":"No data found with key {}".format(title)})
            response = {"data":store,"status":True}
            return responseSender(response)
        else:
            response = {"message":"searching parameter is missing","status":False}
            return responseSender(response), 422
    except:
        response = {"message": "something went wrong", "status": False}
        return responseSender(response) ,500


if __name__ == "__main__":
    db.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://{}:{}@{}/{}".format(str(os.environ.get("DATA_USER_NAME")), str(os.environ.get("DATA_BASE_PASSWORD")),str(os.environ.get("DATA_BASE_HOSTID")),str(os.environ.get("DATA_BASE_NAME")))
    with app.app_context():
        db.create_all()
    app.run(debug=True)