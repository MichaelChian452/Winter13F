import xml.etree.ElementTree as ET

namespaces = {'place': 'http://www.sec.gov/edgar/document/thirteenf/informationtable',
'other_thing': 'http://www.w3.org/2001/XMLSchema-instance'}
stocks = []
#dont use this file

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

def main():
    parse()

if __name__ == "__main__":
    main()
