import xml.etree.ElementTree as ET
import urllib.request
from flask import Flask, render_template, request, url_for

#finding the path to the app directory so that import xmlparser knows which directory to look in
import sys
from pathlib import Path
file = Path(__file__).resolve()
app_directory = file.parents[0]
sys.path.append(str(app_directory))

import xmlparser


app = Flask(__name__)

def listToString(l):
    s = "\n"
    return s.join(l)

def printText(request, url1, url2):
    fulltext = "1st link (old): " + url1 + "\nDate 1: " + request.form["date1"] + "\n2nd link (new): " + url2 + "\nDate 2: " + request.form["date2"] + "\n"
    fulltext += listToString(request.changeOutput)
    fulltext += "\n"
    fulltext += listToString(request.output)
    return fulltext

#@app.route("/", methods=["POST", "GET"])
#def index():
#    parse()


found1 = []
found2 = []
# 0 = not found, 1 = found

def compare(request):
    bought = []
    sold = []
    same = []

    copy1 = request.allHoldings[0].copy()
    copy2 = request.allHoldings[1].copy()
    listing = ""

    for stock in request.allHoldings[0]:
        for s in request.allHoldings[1]:
            if stock["name"] == s["name"]:
                found1.append(1)
                change = stock["amount"] - s["amount"]
                changes = {
                    "name": stock["name"],
                    "change": abs(change),
                    "isAll": False,
                    "amount": stock["amount"]
                }
                listing = stock["name"] + "\t" + "{:,}".format(stock["amount"]) + "\t" + stock["date"] + "\t" + "{:,}".format(s["amount"]) + "\t" + s["date"] + "\t"
                if change < 0:
                    listing += "BUY"
                    bought.append(changes)
                elif change > 0:
                    listing += "SELL"
                    sold.append(changes)
                else:
                    listing += "NC"
                    same.append(changes)
                copy1.remove(stock)
                copy2.remove(s)
                request.output.append(listing)
                break
    #print("checking for new ones")
    for stock in copy1:
        #print(stock)
        changes = {
            "name": stock["name"],
            "change": stock["amount"],
            "isAll": True,
            "amount": stock["amount"]
        }
        listing = stock["name"] + "\t" + "{:,}".format(stock["amount"]) + "\t" + stock["date"] + "\t0\t" + request.allHoldings[1][0]["date"] + "\t"
        listing += "LIQUIDATE"
        request.output.append(listing)
        sold.append(changes)
    for stock in copy2:
        changes = {
            "name": stock["name"],
            "change": stock["amount"],
            "isAll": True,
            "amount": stock["amount"]
        } 
        listing = stock["name"] + "\t0\t" + request.allHoldings[0][0]["date"] + "\t" + "{:,}".format(stock["amount"]) + "\t" + stock["date"] + "\t"
        listing += "INITIATE"
        request.output.append(listing)
        bought.append(changes)
    request.changeOutput.append("-------------------------------------------\nALL STOCKS THAT WERE BOUGHT BETWEEN HOLDING 1 AND HOLDING 2")
    request.changeOutput.append("Company\tHoldings")
    for stock in bought:
        s = stock["name"] + "\t" + "{:,}".format(stock["change"])
        if stock["isAll"] == True:
            s += "\t(New company)"
        request.changeOutput.append(s)

    request.changeOutput.append("-------------------------------------------\nALL STOCKS THAT WERE SOLD BETWEEN HOLDING 1 AND HOLDING 2")
    request.changeOutput.append("Company\tHoldings")
    for stock in sold:
        s = stock["name"] + "\t" + "{:,}".format(stock["change"])
        if stock["isAll"] == True:
            s += "\t(All stocks of that company)"
        request.changeOutput.append(s)
    
    request.changeOutput.append("-------------------------------------------\nNO CHANGE BETWEEN HOLDING 1 AND HOLDING 2")
    request.changeOutput.append("Company\tHoldings")
    for stock in same:
        request.changeOutput.append(stock["name"] + "\t" + "{:,}".format(stock["amount"]))
    
    request.output.append("Company\tHoldings")
    request.output.append("-------------------------------------------")
    request.output.reverse()

@app.route("/", methods=["POST", "GET"])
def primary():
    #parseXML()
    if request.method == "POST":
        request.allHoldings = []
        request.stocks = []
        request.output = []
        request.changeOutput = []
        url1 = request.form["link1"]
        url2 = request.form["link2"]
        #url1 = "https://www.sec.gov/Archives/edgar/data/1067983/000095012320009058/960.xml"
        xmlparser.parseWeb(request, url1, request.form["date1"])
        #url2 = "https://www.sec.gov/Archives/edgar/data/1067983/000095012320012127/0000950123-20-012127-1653.xml"
        xmlparser.parseWeb(request, url2, request.form["date2"])
        compare(request)
        fulltext = printText(request, url1, url2)
        return render_template("index.html", table=fulltext)
    else:
        return render_template("index.html", table="")

if __name__ == "__main__":
    app.run(debug=True)