from flask import Flask, jsonify, request
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
import requests

import pymongo

app = Flask(__name__)

@app.route("/review", methods=['POST'])
def getReviews():
    try:
        searchString = request.json['searchTerm']
        print(searchString)
        dbConnection = pymongo.MongoClient("mongodb://localhost:27017/")
        db = dbConnection['reviews']
        reviews = db[searchString].find({})
        if reviews.count() > 0:
            arrReviews = []
            for review in reviews:
                name = review["name"]
                comment = review["comment"]
                rating = review["rating"]
                dict = {"name": name, "comment": comment, "rating": rating}
                arrReviews.append(dict)
            return {"response" :arrReviews}
        else:
            url = "https://www.flipkart.com/search?q=" + searchString
            client = urlopen(url)
            flipkartPage = client.read()
            client.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            boxes = flipkart_html.findAll("div", {"class": "bhgxx2 col-12-12"})
            del boxes[0:2]
            box = boxes[0]
            # box
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            # productLink
            prodDesc = requests.get(productLink)
            prodDesc.encoding = 'utf-8'
            prodHtml = bs(prodDesc.text, "html.parser")
            reviews = prodHtml.findAll("div", {'class': "_3nrCtb"})
            review = reviews[0]
            table = db[searchString]
            arrReviews = []
            for rev in reviews:
                try:
                    rating = rev.div.div.findAll("div", {"class": "hGSR34 E_uFuv"})[0].text
                    comment = rev.div.div.findAll("p", {"class": "_2xg6Ul"})[0].text
                    customerName = rev.findAll('div', {"class": "row _2pclJg"})[0]
                    name = customerName.div.findAll('p', {'class': '_3LYOAd _3sxSiS'})[0].text
                    print(name + " quotes: " + comment + ". He also rates the product " + rating + " out of 5 \n")
                    dict = {"name": name, "comment": comment, "rating": rating, "product": productLink}
                    table.insert_one(dict)
                    arrReviews.append(dict)
                    # return {"name": name, "comment": comment, "rating": rating, "product": productLink}
                except:
                    print("Skipping")
            return {"responsee" : arrReviews}
    except:
        return "Something went wrong"

if __name__ == '__main__':
    app.run(debug=True)