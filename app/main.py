import xml.etree.ElementTree as ET
import urllib.request
from flask import Flask, render_template, session, request, send_file, Response, redirect, url_for, flash

app = Flask(__name__)

namespaces = {'place': 'http://www.sec.gov/edgar/document/thirteenf/informationtable',
'other_thing': 'http://www.w3.org/2001/XMLSchema-instance'}

def listToString(l):
    s = "\n"
    return s.join(l)

#@app.route("/", methods=["POST", "GET"])
#def index():
#    parse()

def parseWeb(request, url, date):
    response = urllib.request.urlopen(url).read()
    tree = ET.fromstring(response)
    for stock in tree.findall('place:infoTable', namespaces):
        name = stock.find('place:nameOfIssuer', namespaces).text
        amount = stock.find('place:shrsOrPrnAmt', namespaces).find('place:sshPrnamt', namespaces).text
        clss = stock.find('place:titleOfClass', namespaces).text
        #if 
        each = {
            "name": name,
            "amount": int(amount),
            "class": clss,
            "date": date
        }
        inList = False
        pos = 0
        for stock in request.stocks:
            if stock['name'] == each['name']:
                inList = True
                pos = request.stocks.index(stock)
                break
        if inList:
            request.stocks[pos]['amount'] = request.stocks[pos]['amount'] + each['amount']
        else:
            request.stocks.append(each)
    request.allHoldings.append(request.stocks.copy())
    request.output.append("Company\tHoldings")
    for stock in request.stocks:
        request.output.append(stock["name"] + "\t" + "{:,}".format(stock["amount"]) + "\t" + stock["date"])
    request.stocks.clear()

found1 = []
found2 = []
# 0 = not found, 1 = found

def compare(request):
    bought = []
    sold = []
    same = []

    copy1 = request.allHoldings[0].copy()
    copy2 = request.allHoldings[1].copy()

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
                if change < 0:
                    sold.append(changes)
                elif change > 0:
                    bought.append(changes)
                else:
                    same.append(changes)
                copy1.remove(stock)
                copy2.remove(s)
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
        sold.append(changes)
    for stock in copy2:
        changes = {
            "name": stock["name"],
            "change": stock["amount"],
            "isAll": True,
            "amount": stock["amount"]
        } 
        bought.append(changes)
    request.changeOutput.append("-------------------------------------------\nALL STOCKS THAT WERE BOUGHT BETWEEN HOLDING 1 AND HOLDING 2")
    request.changeOutput.append("Company\tHoldings")
    spaces = ""
    for stock in bought:
        for n in range(35 - len(stock["name"])):
            spaces += " "
        s = stock["name"] + "\t" + "{:,}".format(stock["change"])
        if stock["isAll"] == True:
            s += "\t(New company)"
        request.changeOutput.append(s)
        spaces = ""

    request.changeOutput.append("-------------------------------------------\nALL STOCKS THAT WERE SOLD BETWEEN HOLDING 1 AND HOLDING 2")
    request.changeOutput.append("Company\tHoldings")
    for stock in sold:
        for n in range(35 - len(stock["name"])):
            spaces += " "
        s = stock["name"] + "\t" + "{:,}".format(stock["change"])
        if stock["isAll"] == True:
            s += "\t(All request.stocks of that company)"
        request.changeOutput.append(s)
        spaces = ""
    
    request.changeOutput.append("-------------------------------------------\nNO CHANGE BETWEEN HOLDING 1 AND HOLDING 2")
    request.changeOutput.append("Company\tHoldings")
    for stock in same:
        for n in range(35 - len(stock["name"])):
            spaces += " "
        request.changeOutput.append(stock["name"] + "\t" + "{:,}".format(stock["amount"]))
        spaces = ""

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
        request.output.append("The first holding (" + url1 + "):")
        parseWeb(request, url1, request.form["date1"])
        #url2 = "https://www.sec.gov/Archives/edgar/data/1067983/000095012320012127/0000950123-20-012127-1653.xml"
        request.output.append("The second holding (" + url2 + "):")
        parseWeb(request, url2, request.form["date2"])
        compare(request)
        fulltext = listToString(request.changeOutput)
        fulltext += "\n"
        fulltext += listToString(request.output)

        return render_template("index.html", table=fulltext)
    else:
        return render_template("index.html", table="")

if __name__ == "__main__":
    app.run(debug=True)