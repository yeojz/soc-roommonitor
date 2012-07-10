#!/usr/bin/python 

from bs4 import BeautifulSoup
import urllib

endpoint = 'http://137.132.5.219:8001/reporting/individual?objectclass=location&idtype=id&identifier=%s&t=SWSCUST+location+individua1-7&weeks=&periods=1-30&template=SWSCUST+location+individual'
rooms = ['COM1/201', 'COM1/202']
day = 0


f = urllib.urlopen("http://localhost/campus/roombooking/test.html")
html = f.read()




#parsing
soup = BeautifulSoup(''.join(html))
#print soup.prettify()



tables = soup.findAll('table', bgcolor="#FFFFFF", border="0",cellspacing="0",width="100%")


for table in tables:
	rows = table.findAll('tr')
	for tr in rows:
		cols = tr.findAll('td')
	 	for td in cols:
			print td.get_text()

		
		
		
#formatting





#dumping





