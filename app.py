import xml.etree.ElementTree as ET
from flask import Flask, render_template, session, request, send_file, Response, redirect, url_for, flash
from flask_session import Session

#app = Flask(__name__)

namespaces = {'place': 'http://www.sec.gov/edgar/document/thirteenf/informationtable',
'other_thing': 'http://www.w3.org/2001/XMLSchema-instance'}
stocks = []

def parse():
    root = ET.parse('0000950123-20-012127-1653.xml').getroot()
    for stock in root.findall('place:infoTable', namespaces):
        name = stock.find('place:nameOfIssuer', namespaces).text
        amount = stock.find('place:shrsOrPrnAmt', namespaces).find('place:sshPrnamt', namespaces).text
        each = {
            "name": name,
            "amount": int(amount)
        }
        inList = False
        pos = 0
        for stock in stocks:
            if stock['name'] == each['name']:
                inList = True
                pos = stocks.index(stock)
                break
        if inList:
            stocks[pos]['amount'] = stocks[pos]['amount'] + each['amount']
        else:
            stocks.append(each)
    print(stocks)
    spaces = ""
    file = open("data.txt", "w")
    file.write("Company                            Holdings\n")
    for stock in stocks:
        for n in range(35 - len(stock["name"])):
            spaces += " "
        file.write(stock["name"] + spaces + str(stock["amount"]) + "\n")
        spaces = ""
    file.close()

#@app.route("/", methods=["POST", "GET"])
#def index():
#    parse()

def main():
    parse()

#if __name__ == "__main__":
#    app.run(debug=True)

if __name__ == "__main__":
    main()