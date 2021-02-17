import xml.etree.ElementTree as ET
import urllib.request

namespaces = {'place': 'http://www.sec.gov/edgar/document/thirteenf/informationtable',
'other_thing': 'http://www.w3.org/2001/XMLSchema-instance'}


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
    request.stocks.clear()