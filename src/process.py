import bottlenose
import graphlab as gl
from bs4 import BeautifulSoup
import pandas as pd


class Data():
    def __init__(self):
        self.items = gl.SFrame.read_csv('data/Reviews.csv')
        self.trends = self.items.sort('Time', ascending=False)
        self.db = pd.read_csv('data/db60_75.csv')

    def createModels(self):
        mf = gl.factorization_recommender.create(self.items, user_id='UserId', item_id='ProductId', target='Score')
        mf.save('models/MatrixFac')

        item_item = gl.item_similarity_recommender.create(self.items, user_id='UserId', item_id='ProductId', target='Score')
        item_item.save('models/item-item_CF')

        popular = gl.popularity_recommender.create(self.items, user_id='UserId', item_id='ProductId', target='Score')
        popular.save('models/Popular')

        trending = gl.popularity_recommender.create(self.trends[:5000], user_id='UserId', item_id='ProductId', target='Score')
        trending.save('models/Trending')

    def evaluate(self):
        # train, test = gl.recommender.util.random_split_by_user(self.items, user_id='UserId', item_id='ProductId')
        # m = gl.item_similarity_recommender.create(train, user_id='UserId', item_id='ProductId', target='Score')
        # m.evaluate_rmse(test, target='Score')
        model = gl.load_model('models/Popular')
        model.evaluate(self.items)

    def visualize(self):
        # Start at your instinct
        self.items.show()
        training_data, test_data = self.items.random_split(0.8, seed=0)
        model = gl.load_model("item-model1")
        pred = model.predict(test_data)
        results = model.evaluate(test_data)
        print (results)
        view = model.views.overview(validation_set=test_data)
        view.show()
        gl.evaluation.rmse(self.validation_data)
        view = model.views.overview(validation_set=self.validation_data)
        view.show()

    def queryAmazon(self, prodList,rgp=''):
        amazon = bottlenose.Amazon('', '', '')
        itemdict = []
        db = self.db
        lis = list(db['Item'])
        for item in prodList:
            if item in lis:
                if len(rgp) != 0:
                    value = db[db['Item'] == item]['Image'].values[0]
                else:
                    value = db[db['Item'] == item]['ProductName'].values[0]
            else:
                try:
                    response = amazon.ItemLookup(ItemId=item, ResponseGroup=rgp)
                    soup = BeautifulSoup(response,"xml")
                    if len(rgp) != 0:
                        value = soup.MediumImage.URL.string
                    else:
                        value = soup.ItemAttributes.Title.string
                except:
                    value = ""
                    pass
            itemdict.append(value)
        return itemdict

    def getData(self,reco):
        pn = self.queryAmazon(reco['ProductId'])
        pn = [x.encode('utf-8') if len(x) != 0 else "Some Awesome Product" for x in pn]
        reco.add_column(gl.SArray(pn), name='ProductName')
        rn = self.queryAmazon(reco['ProductId'], 'Images')
        rn = [x.encode('utf-8') if len(x) != 0 else "static/img/default.jpeg" for x in rn]
        reco.add_column(gl.SArray(rn), name='ProductURL')
        reco = reco.pack_columns(columns=['score', 'rank', 'ProductName', 'ProductURL'], new_column_name='Details')
        df = reco.to_dataframe().set_index('ProductId')
        recommendations = df.to_dict(orient='dict')['Details']
        return recommendations

    def mostPopular(self, topk):
        items = self.items
        model = gl.load_model('models/Popular')
        reco = model.recommend_from_interactions(items[items['Score'] > 4].remove_column('UserId'), k=topk,
                                                 items=items[items['Score'] > 2].select_column('ProductId'))
        return self.getData(reco)


    def getRecoForUser(self, user, topk):
        model = gl.load_model('models/MatrixFac')
        reco = model.recommend(users=user,k=topk)
        return self.getData(reco)

    def whatsTrending(self, topk):
        trends = self.trends[:5000]
        model = gl.load_model('models/Trending')
        reco = model.recommend_from_interactions(trends[trends['Score'] > 4][:10].remove_column('UserId'), k=topk,
                                          items=trends[trends['Score'] > 3][100:1100].select_column('ProductId'))
        return self.getData(reco)

    def getSimilarItems(self, item, topk):
        model = gl.load_model('models/item-item_CF')
        reco = model.get_similar_items(items=[item], k=topk)
        reco = reco.remove_column('ProductId').rename({'similar': 'ProductId'})
        return self.getData(reco)

    def getAverageRating(self, item):
        items = self.items
        return items[items['ProductId']==item].select_column('Score').mean()

    def helpfulReviews(self, item, topk):
        items = self.items
        reviews = items[items['ProductId'] == item]
        reviews['helpful'] = reviews['HelpfulnessNumerator']/reviews['HelpfulnessDenominator']
        reviews = reviews.sort(['helpful', 'Time'], ascending=False)[:topk]
        reviews = reviews.to_dataframe().set_index('UserId')
        reviews = reviews.to_dict(orient='dict')
        return reviews

    def userHistory(self, user, topk):
        items = self.items
        reco = items[items['UserId'] == user].sort(['Time'], ascending=False)[:topk]
        pn = self.queryAmazon(reco['ProductId'])
        pn = [x.encode('utf-8') if len(x) != 0 else "Some Awesome Product" for x in pn]
        reco.add_column(gl.SArray(pn), name='ProductName')
        rn = self.queryAmazon(reco['ProductId'], 'Images')
        rn = [x.encode('utf-8') if len(x) != 0 else "static/img/default.jpeg" for x in rn]
        reco.add_column(gl.SArray(rn), name='ProductURL')
        reco = reco.pack_columns(columns=['Score', 'ProductName', 'ProductURL', 'Summary', 'Text'], new_column_name='Details')
        df = reco.to_dataframe().set_index('ProductId')
        user_history = df.to_dict(orient='dict')['Details']
        return user_history

    def getUserName(self, user):
        items = self.items
        return items[items['UserId'] == user].select_column('ProfileName')[0]

    def getAllItems(self):
        items = pd.read_csv('data/names.csv', encoding='utf-8')
        items = items.set_index('0')
        items = items.to_dict(orient='dict')['1']
        return items