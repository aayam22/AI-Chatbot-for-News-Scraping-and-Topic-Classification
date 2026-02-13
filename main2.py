from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import time

def get_jobs():
    html_text = requests.get('https://weworkremotely.com/').text
    soup = BeautifulSoup(html_text,'lxml')
    jobs = soup.find_all('li', class_='new-listing-container feature')
    for index, job in enumerate(jobs):
        published_date = job.find('p', class_='new-listing__header__icons__date').text.replace('\n', '').strip()
        if 'New' in published_date:
            company_name = job.find('p', class_='new-listing__company-name').text.replace('\n', '').strip()
            job_title = job.find('h3', class_='new-listing__header__title').text.replace('\n', '').strip()
            more_info = urljoin('https://weworkremotely.com/', job.a['href'])
            with open(f'post/{index}.txt', 'w') as f:
                f.write(f'Company Name: {company_name}\n')
                f.write(f'Job Title: {job_title}\n')
                f.write(f'More Info: {more_info}\n')
            
            
        

            print('')

if __name__ == '__main__':
    while True:
        get_jobs()
        time_wait = 10
        print(f'Waiting for {time_wait} seconds...')
        time.sleep(time_wait*6)
    

