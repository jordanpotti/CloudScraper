from argparse import ArgumentParser
from multiprocessing import Pool
from termcolor import colored
from rfc3987 import parse
import requests_html
import itertools
import sys


def print_banner():
        print('''\nCloudScraper is a tool to search through the source code of websites in order to find cloud resources belonging to a target.
        by Jordan Potti
        @ok_bye_now\n'''
        )


def start(target):
    '''
        Load the initial url and gather the first urls that will be used
        by the spider to keep looking for more links
    '''
    print(colored("Beginning search for cloud resources in {}".format(target), color='cyan'))

    try:
        html = requests_html.requests.get(target, allow_redirects=True, headers=headers).text
        html = requests_html.HTML(html=html)
        links = list(set(html.absolute_links))

    except requests_html.requests.exceptions.RequestException as e:
        if arguments.v:
            print(colored('Network error: {}'.format(e), 'red', attrs=['bold']))
        return

    print(colored('Initial links: {}\n'.format(len(links)), color='cyan'))
    spider(links, target)


def worker(url):
    '''
        Function handling all the crawling action of the spider.
        It first checks the desired depth and if the domain of
        the url matches the target to avoid crawling other web sites.
        Makes a GET request, parses the HTML and returns all the links.
    '''
    try:
        if (target_['authority'] in parse(url)['authority']) and (url.count("/") < arguments.depth+2):
            try:
                html = requests_html.requests.get(url, allow_redirects=True, headers=headers).text
                html = requests_html.HTML(html=html)
                links = list(set(html.absolute_links))

            except requests_html.requests.exceptions.RequestException as e:
                if arguments.v:
                    print(colored('Network error: {}'.format(e), 'red', attrs=['bold']))
                return []

            print('{} links found [{}]'.format(len(links), url))
            return links

        else:
            return []

    #errors thrown by the url parser if the given url is invalid
    except ValueError:
        if arguments.v:
            print(colored('Error: {}'.format(url), 'red', attrs=['bold']))
        return []
    
    except TypeError:
        if arguments.v:
            print(colored('Error: {}'.format(url), 'red', attrs=['bold']))
        return []
        

def spider(base_urls, target):
    '''
        Loop through the initial links found in the given page. Each new link
        discovered will be added to the list if it's not already there, and thus
        crawled aswell looking for more links.

        wannabe list works as the placeholder for the urls that are yet to crawl.
        base_urls is a list with all the already crawled urls.
    '''
    global target_
    target_ = parse(target)
    p = Pool(arguments.process)
    wannabe = base_urls 

    while True:
        #retrieve all the urls returned by the workers
        new_urls = p.map(worker, wannabe)
        #flatten them and remove repeated ones
        new_urls = list(set(itertools.chain(*new_urls)))
        wannabe = []
        i = 0

        #if new_urls is empty meaning no more urls are being discovered, exit the loop
        if new_urls == []:
            break
        
        else:
            for url in new_urls:
                if url not in base_urls:
                    '''
                    For each new url, check if it hasn't been crawled. If it's indeed new,
                    it gets appended to the wannabe list so in the next iteration it will be crawled. 
                    '''
                    i += 1
                    wannabe.append(url)
                    base_urls.append(url)
        
        print(colored('\nNew urls appended: {}\n'.format(i), 'green', attrs=['bold']))

    #once all the links for the given depth have been analyzed, execute the parser
    parser(base_urls)


def parser(links):
    '''
        Once all the links have been gathered check how many of them
        match with the list of cloud domains we are interested in.
    '''
    print(colored('Parsing results...', 'cyan', attrs=['bold']))
    cloud_domains = ['amazonaws.com', 'digitaloceanspaces.com', 'windows.net']
    matches = []

    [[matches.append(link) for link in links if cloud_domain in link] for cloud_domain in cloud_domains]
    matches = list(set(matches))
    
    print('\nTotal links: ', len(links))
    if len(matches) == 0:
        print(colored("There were no matches!", 'red', attrs=['bold']))
    
    else:
        print(colored("There were {} matches for this search!".format(len(matches)), 'green', attrs=['bold']))
        [print(match, "\n") for match in matches]


def args():
    parser = ArgumentParser()
    parser.add_argument("-u", dest="URL", required=False, help="Target Scope") 
    parser.add_argument("-d", dest="depth", type=int, required=False, default=25, help="Max Depth of links Default: 25")
    parser.add_argument("-l", dest="targetlist", required=False, help="Location of text file of Line Delimited targets") 
    parser.add_argument("-v", action="store_true", default=False, required=False, help="Verbose output")
    #parser.add_argument("-t", dest="time", required=False, default=0, help="Time between GETs to avoid getting blocked")
    parser.add_argument("-p", dest="process", required=False, default=2, type=int, help="Number of processes to run")
    if len(sys.argv) == 1:
        parser.error("No arguments given.")
        parser.print_usage
        sys.exit()

    #ouput parsed arguments into a usable object
    return parser.parse_args()


def cleaner(url):
    if 'http' not in url:
        return ("https://"+url).rstrip()
    else:
        return url


def main():
    if arguments.targetlist:
        with open (arguments.targetlist, 'r') as target_list:
            [start(cleaner(line)) for line in target_list]
    else:
        start(cleaner(arguments.URL))


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'}
arguments = args()

if __name__ == '__main__':
    print_banner()
    main()
