from requests_html import HTMLSession
from argparse import ArgumentParser
from termcolor import colored
from rfc3987 import parse
import sys

def print_banner():
        print('''\n
        CloudScraper is a tool to search through the source code of websites in order to find cloud resources belonging to a target.
        by Jordan Potti
        @ok_bye_now
        (forked by Turr0n)
        \n'''
        )   

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
          }


def start(target, depth):
    '''
        Load the initial url and gather the first urls that will be used
        by the spider to keep looking for more links
    '''
    s = HTMLSession()

    print(colored("Beginning search for cloud resources in {}".format(target), color='cyan'))
    html = s.get(target, allow_redirects=True, headers=headers).html
    
    links = list(html.absolute_links)
    print(colored('Initial links: {}\n'.format(len(links)), color='cyan'))

    spider(links, target, depth, s)
    
def worker(target_, depth, url, s):
    '''
        
        
    '''
    try:
        if (target_['authority'] in parse(url)['authority']) and url.count("/") < depth+2:
            html = s.get(url, allow_redirects=True, headers=headers).html
            links = html.absolute_links
                
            #if verbose output is activated, print a bit more information
            if arguments.v:
                print('\n{} links found [{}]'.format(len(links), url))
                
            return links

    except ValueError or TypeError:
        #error thrown by the url parser if the given url is invalid
        pass
        

def spider(links, target, depth, s):
    '''
        Loop through the initial links found in the given page. Each new link
        discovered will be added to the list if it's not already there, and thus
        crawled aswell looking for more links.
    '''
    target_ = parse(target) #more appropiate way to get the domain for later use in the worker function

    for url in links:
        old_len = len(links)
        new_links = worker(target_, depth, url, s)
        
        try:
            #loop through new_links and add them to links if they haven't been seen yet
            [links.append(link) for link in new_links if link not in links]
            
            if len(links)-old_len != 0:
                print(colored('[+] Added links: {} [Total: {}]'.format(len(links)-old_len, len(links)), 'green'))
        except TypeError:
            pass

    #once all the links for the given depth have been analyzed, execute the parser
    parser(links)


def parser(links):
    '''
        Once all the links have been gathered check how many of them
        match with the list of cloud domains we are interested in.
    '''
    print('Total links: ', len(links))
    
    matches = []
    cloud_domains = ['amazonaws.com', 'digitaloceanspaces.com', 'windows.net']

    [[matches.append(link) for link in links if cloud_domain in link] for cloud_domain in cloud_domains]
    matches = list(set(matches))
    
    if len(matches) == 0:
        print(colored("There were no matches!", 'red'))
    
    else:
        print(colored("\nThere were {} matches for this search!".format(len(matches)), 'green'))
        for match in matches:
            print(match, "\n")

def args():
    parser = ArgumentParser()
    parser.add_argument("-u", dest="URL", required=False, help="Target Scope") 
    parser.add_argument("-d", dest="depth", type=int, required=False, default=25, help="Max Depth of links Default: 25")
    parser.add_argument("-l", dest="targetlist", required=False, help="Location of text file of Line Delimited targets") 
    parser.add_argument("-v", action="store_true", default=False, required=False, help="Verbose output")

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
            [start(cleaner(line), arguments.depth) for line in target_list]
    else:
        start(cleaner(arguments.URL), arguments.depth)

global arguments
arguments = args()

print_banner()
main()
