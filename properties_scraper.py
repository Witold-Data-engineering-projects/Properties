from urllib.request import Request, urlopen
from bs4 import BeautifulSoup as soup
import datetime
import pandas as pd
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import math
from itertools import cycle
from sqlalchemy.sql import text


URLS2 = {'Nuneaton': 'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E1020&index=',
         'Leicester':'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E789&index=',
         'Peterborough':'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E1061&index=',
         'Hinckley':'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E640&index=',
         'Telford':'https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E1323&index='}

type = '&propertyTypes=bungalow%2Cdetached%2Csemi-detached%2Cterraced&maxDaysSinceAdded=14&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords='

now = str(datetime.date.today())
print (now)

def pages(url):
    Area = Request(url =url+type,
               headers={'User-Agent': 'Mozilla/5.0'}
               )
    uClient = urlopen(Area)
    page_html = uClient.read()
    uClient.close()
    page_soup = soup(page_html, "html.parser")
    number_of_properies = page_soup.find("span", {"class":"searchHeader-resultCount"}).text.replace(",","")
    print('number of properties = '+ number_of_properies)
    number_of_pages = math.floor(int(number_of_properies)/24)+1
    return number_of_pages


def fetch(url):

    header = ['Title', 'Address', 'Price', 'Updated', 'Snip','Date','Bedrooms']
    global propertyinfo
    propertyinfo = pd.DataFrame(columns=header)
    index = 0
    num_pages = pages(url)

    for i in range (num_pages):

        index = str(index)
        Area = Request(url=url + index + type,
               headers={'User-Agent': 'Mozilla/5.0'}
               )
        uClient = urlopen(Area)
        page_html = uClient.read()
        uClient.close()
        page_soup = soup(page_html, "html.parser")
        wrapers = page_soup.findAll("div", {"class":"propertyCard-wrapper"})

        print (i)
        index = int(index)
        index = index +24

        #collecting 
        for wraper in wrapers:

            title = wraper.find("h2", {"class":"propertyCard-title"}).text.replace("\n","")
            address = wraper.find("address",{"class":"propertyCard-address"}).text.replace("\n","")
            price = wraper.find("div", {"class": "propertyCard-priceValue"}).text.replace("Â","")
            updated_by = wraper.find("div",{"class":"propertyCard-branchSummary"}).text.replace("\n","")
            snip = wraper.find("span",{"itemprop":"description"}).text.replace("\n","")
            # link extraction
            linkpres = wraper.find("a", class_ = "propertyCard-img-link",attrs={"data-test": "property-img"})
            link_pro = linkpres["href"]
            start_html = "https://www.rightmove.co.uk"
            linkfull = start_html+link_pro
           


            new_row = {'Title': title, 'Address': address, 'Price': price, 'Updated': updated_by, 'Snip': snip,'Link':linkfull}
            propertyinfo =  pd.concat([propertyinfo, pd.DataFrame([new_row])], ignore_index=True)

#splitting and cleaning
    propertyinfo['Street']= propertyinfo.Address.str.split(",").str[0]
    propertyinfo['Street']= propertyinfo.Street.str.replace(' ', '-', regex=True)

    propertyinfo['Town']= propertyinfo.Address.str.split(",").str[1]
    propertyinfo['Price']= propertyinfo.Price.replace({"Â",""},regex=True)
    propertyinfo['Date']= now
    propertyinfo['Bedrooms']= [x[:14] for x in propertyinfo['Title']]
    propertyinfo = propertyinfo[propertyinfo['Town'].notna()]
    propertyinfo = propertyinfo.replace('Â','',regex=True)
    propertyinfo = propertyinfo
    return propertyinfo



def connection():
    engine = sqlalchemy.create_engine("mysql+pymysql://root:Blindman6@192.168.1.87:3307/Properties")
    Session = sqlalchemy.orm.sessionmaker()
    Session.configure(bind=engine)
    session = Session
    return engine

engine = connection()


for key in URLS2:
    Town = (key)
    file_name = (key)
    print (Town)
    Town = fetch(URLS2[key])
    Town.to_csv(file_name+'.csv')
    #Town.to_sql(file_name,con=engine,if_exists="append",index=False)




'''
with engine.connect() as con:
    statement = text("""DROP TABLE Nuneaton""")
    rs = con.execute(statement)
    #for row in rs:
    #    print (row)

'''
''' 
random changes2
'''


