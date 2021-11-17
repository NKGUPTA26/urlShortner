from hashids import Hashids
from flask import Flask, request, flash, redirect, url_for,Response
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
        soup = BeautifulSoup(response.text)
        metas = soup.find_all('meta')
        title = soup.find("meta",  property="og:title")
        print(title["content"])
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
        url_details.meta = str([meta.attrs['content'] for meta in metas if 'name' in meta.attrs and meta.attrs['name'] == 'description'][0])
        db.session.commit()
        response = {"success": True, "short_url":short_url}
        return responseSender(response)

@app.route('/<id>',methods = ["GET"])
def url_redirect(id):
    original_id = hashids.decode(id)
    if original_id:
        original_id = original_id[0]
        url = Url.query.filter_by(id=original_id).first()
        original_url = url.original_url
        clicks = url.total_clicks
        updateDetails = Url.query.filter_by(id=original_id).first()
        updateDetails.total_clicks += 1
        click_data = Clicks(url_id = original_id , url_click_at_time = 1)
        db.session.add(click_data)
        db.session.commit()
        response = {"success": True}
        return redirect(original_url)
    else:
        flash('Invalid URL')
        return redirect(url_for('index'))


if __name__ == "__main__":
    db.init_app(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://{}:{}@{}/test".format(str(os.environ.get("DATA_USER_NAME")), str(os.environ.get("DATA_BASE_PASSWORD")),str(os.environ.get("DATA_BASE_HOSTID")))
    with app.app_context():
        db.create_all()
    app.run(debug=True)