import xml.etree.ElementTree as ET
import urllib.request

#app = Flask(__name__)

namespaces = {'place': 'http://www.sec.gov/edgar/document/thirteenf/informationtable',
'other_thing': 'http://www.w3.org/2001/XMLSchema-instance'}
allHoldings = []
stocks = []

def parseXML():
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
    file = open("data.txt", "a")
    file.write("yeet\n")
    file.write("Company                            Holdings\n")
    for stock in stocks:
        for n in range(35 - len(stock["name"])):
            spaces += " "
        file.write(stock["name"] + spaces + "{:,}".format(stock["amount"]) + "\n")
        spaces = ""
    file.close()

#@app.route("/", methods=["POST", "GET"])
#def index():
#    parse()

def parseWeb(url):
    response = urllib.request.urlopen(url).read()
    tree = ET.fromstring(response)
    for stock in tree.findall('place:infoTable', namespaces):
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
    allHoldings.append(stocks.copy())
    spaces = ""
    file = open("data.txt", "a")
    file.write("Company                            Holdings\n")
    for stock in stocks:
        for n in range(35 - len(stock["name"])):
            spaces += " "
        file.write(stock["name"] + spaces + "{:,}".format(stock["amount"]) + "\n")
        spaces = ""
    file.close()
    stocks.clear()

def compare():
    bought = []
    sold = []
    same = []
    for stock in allHoldings[0]:
        for s in allHoldings[1]:
            if stock["name"] == s["name"]:
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
                allHoldings[0].remove(stock)
                allHoldings[1].remove(s)
                break
    #print("checking for new ones")
    for stock in allHoldings[0]:
        #print(stock)
        changes = {
            "name": stock["name"],
            "change": stock["amount"],
            "isAll": True,
            "amount": stock["amount"]
        }
        sold.append(changes)
    for stock in allHoldings[1]:
        changes = {
            "name": stock["name"],
            "change": stock["amount"],
            "isAll": True,
            "amount": stock["amount"]
        } 
        bought.append(changes)
    file = open("data.txt", "a")
    file.write("-------------------------------------------\nALL STOCKS THAT WERE BOUGHT BETWEEN HOLDING 1 AND HOLDING 2\n")
    file.write("Company                            Holdings\n")
    spaces = ""
    for stock in bought:
        for n in range(35 - len(stock["name"])):
            spaces += " "
        file.write(stock["name"] + spaces + "{:,}".format(stock["change"]))
        if stock["isAll"] == True:
            file.write(" (New company)")
        file.write("\n")
        spaces = ""

    file.write("-------------------------------------------\nALL STOCKS THAT WERE SOLD BETWEEN HOLDING 1 AND HOLDING 2\n")
    file.write("Company                            Holdings\n")
    for stock in sold:
        for n in range(35 - len(stock["name"])):
            spaces += " "
        file.write(stock["name"] + spaces + "{:,}".format(stock["change"]))
        if stock["isAll"] == True:
            file.write(" (All stocks of that company)")
        file.write("\n")
        spaces = ""
    
    file.write("-------------------------------------------\nNO CHANGE BETWEEN HOLDING 1 AND HOLDING 2\n")
    file.write("Company                            Holdings\n")
    for stock in same:
        for n in range(35 - len(stock["name"])):
            spaces += " "
        file.write(stock["name"] + spaces + "{:,}".format(stock["amount"]))
        file.write("\n")
        spaces = ""
    file.close()


def main():
    #parseXML()

    print("Paste link to first xml file: ")
    url1 = input()
    #url1 = "https://www.sec.gov/Archives/edgar/data/1067983/000095012320009058/960.xml"
    file = open("data.txt", "w")
    file.write("The first holding:\n")
    file.close()
    parseWeb(url1)
    print("Paste link to second xml file:")
    url2 = input()
    #url2 = "https://www.sec.gov/Archives/edgar/data/1067983/000095012320012127/0000950123-20-012127-1653.xml"
    file = open("data.txt", "a")
    file.write("The second holding:\n")
    file.close()
    parseWeb(url2)
    compare()

#if __name__ == "__main__":
#    app.run(debug=True)

if __name__ == "__main__":
    main()