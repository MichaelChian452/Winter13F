import xml.etree.ElementTree as ET


def parse():
    root = ET.parse('0000950123-20-012127-1653.xml').getroot()
    for stock in root.findall('infoTable'):
        name = stock.find('nameOfIssuer').text