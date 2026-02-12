from bs4 import BeautifulSoup
import requests

html_text = requests.get('https://weworkremotely.com/').text

print(html_text)
soup = BeautifulSoup(html_text,'lxml')
