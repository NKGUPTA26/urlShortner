Before runing the application install python3 in your system

set up a virtual environment for the project:
python3 -m venv venv

Activate the environment:
source venv/bin/activate

Install the dependencies:
pip install -r requirements.txt

To Run the app:
pyhton3 app.py

1. For url shortner api
You can do curl 
curl --location --request POST 'http://127.0.0.1:5000/' \
--form 'url="{replace this with url you want to shorten}"'
curl --location --request POST 'https://github.com/NKGUPTA26"'

2.To get the meta data of tiny url
you can do curl
curl --location --request GET '{replace this with tiny url you get in response form first api}?meta=true'
e.g:- curl --location --request GET 'http://127.0.0.1:5000/xaZ3?meta=true'

3. If you hit tiny url it will redirect you the original url

4. API to find all pages which have a partial or full match for the passed term.
you can do curl
curl --location --request GET 'http://127.0.0.1:5000/search/{keyword}'
eg.-curl --location --request GET 'http://127.0.0.1:5000/search/python'

