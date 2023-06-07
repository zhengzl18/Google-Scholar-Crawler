import csv
import re
import time

import requests
from fp.errors import FreeProxyException
from fp.fp import FreeProxy
from scholarly import ProxyGenerator
from scholarly import scholarly as S


class MyFreeProxy(FreeProxy):
    def __init__(self, country_id=None, timeout=0.5, rand=False, anonym=False, elite=False, google=None, https=False):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        self.anonym = anonym
        self.elite = elite
        self.google = google
        self.schema = 'https' if https else 'http'

    def get_proxy_list(self, repeat):
        try:
            page = requests.get(self.__website(repeat))
        except requests.exceptions.RequestException as e:
            raise FreeProxyException(
                f'Request to {self.__website(repeat)} failed') from e

        try:
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', page.text)
            proxies = [':'.join(proxy) for proxy in proxies]
            return proxies
        except Exception as e:
            raise FreeProxyException('Failed to get list of proxies') from e

    def __website(self, repeat):
        return "https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1"


S.set_logger(True)

def _set_new_proxy():
    pg = ProxyGenerator()
    while True:
        proxy = MyFreeProxy(rand=True, timeout=1).get()
        success = pg.SingleProxy(http=proxy, https=proxy)
        if success:
            break
    print("Working proxy:", proxy)
    return proxy

def crawl_abstracts(keyword, year_low=None, year_high=None, outfile=None, max_iter=1000):
    _set_new_proxy()
    while True:
        try:
            search_query = S.search_pubs(keyword, year_low=year_low, year_high=year_high)
            time.sleep(5)
            break
        except Exception as e:
            print(e)
            print("Trying new proxy on query base")
            _set_new_proxy()

    print("Crawling Started with keyword <" + keyword + ">.\n")

    if not outfile:
        outfile = "[Crwaling Results]" + keyword + ".csv"

    with open(outfile, 'w') as o_file:
        w = csv.writer(o_file)

        header = "Index, Year, Author, Title, abstract\n"
        o_file.write(header)

        idx = 0
        for _ in range(max_iter):
            while True:
                try:
                    time.sleep(5)
                    article = next(search_query)['bib']
                    break
                except Exception as e:
                    print(e)
                    print("Trying new proxy on article read")
                    _set_new_proxy()

            try:
                title = article["title"]
            except KeyError:
                print("Error on Title Info")
                continue

            try:
                abstract = article["abstract"]
                if abstract.startswith("Skip to main content"):
                    continue
            except KeyError:
                print("Error on Abstract")
                continue

            try:
                year = article["pub_year"]
            except KeyError:
                print("Error on year")
                continue

            try:
                author = article["author"]
            except KeyError:
                print("Error on author")
                continue

            idx += 1

            citation_form = ','.join(author) + '. "' + title + '." ' + year
            print(f"\n{idx}. {citation_form}")
            w.writerow([str(idx), year, ','.join(author), title, abstract])


    print("\n\nProcess Done!")
    print(f"{idx} articles are crawled.")
    print(f"Results are saved in <{outfile}>.")


if __name__ == "__main__":
    keywords = "source:management source:Communication source:Quarterly" # The keywords for searching. This is an example for searching papers on the journal "Management Communication Quarterly".
    year_low = 2012
    year_high = None
    outfile = None
    max_iter = 1000
    crawl_abstracts(
        keywords, 
        year_low=year_low, 
        year_high=year_high,
        outfile=outfile, 
        max_iter=max_iter
    )