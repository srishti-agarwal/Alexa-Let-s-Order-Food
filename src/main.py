from flask import Flask, render_template, request
from process import Data
import sys

app = Flask(__name__)
data = Data()

@app.route("/", methods=['GET','POST'])
def welcome():
    popular = data.whatsTrending(20)
    u_popular = {k: [str(i).decode('utf8') for i in v if str(type(i)=="<type 'unicode'>")] for k, v in popular.items()}
    ids = data.getAllItems()
    return render_template('index.html', popular=u_popular, data=ids)


@app.route("/recommend", methods=['GET','POST'])
def user():
    username = request.args.get('user')
    if username == 'query': username = request.form['username']
    profilename = data.getUserName(username)
    reco = data.getRecoForUser([username], 10)
    u_reco = {k: [str(i).decode('utf8') for i in v if str(type(i)=="<type 'unicode'>")] for k, v in reco.items()}
    history = data.userHistory(username, 10)
    hist = {k: [str(i).decode('utf8') for i in v if str(type(i)=="<type 'unicode'>")] for k, v in history.items()}
    return render_template('recommendations.html', user=profilename, reco=u_reco, hist=hist)

@app.route("/item", methods=['GET','POST'])
def item():
    item = request.args.get('item')
    if item == 'query': item = request.form['item']
    name = data.queryAmazon([item])[0]
    img_url = data.queryAmazon([item], 'Images')[0]
    rating = data.getAverageRating(item)
    similar = data.getSimilarItems(item, 10)
    u_simi = {k: [str(i).decode('utf8') for i in v if str(type(i)=="<type 'unicode'>")] for k, v in similar.items()}
    helpful = data.helpfulReviews(item, 5)
    return render_template('item.html', id=item, name=name, url=img_url, rating=rating, similar=u_simi, helpful=helpful)

if __name__ == '__main__':
    if len(sys.argv)==2 and sys.argv[1] == 'create':
        data.createModels()
    elif len(sys.argv)==2 and sys.argv[1] == 'debug':
        app.debug = True
        app.run(threaded=True)
    else:
        app.run(threaded=True)