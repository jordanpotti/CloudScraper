import requests
import re
from argparse import ArgumentParser
import sys
from bs4 import BeautifulSoup

grep_list = None

arguments = None

def print_banner():
        print('''\nDescription: 
        CloudScraper is a tool to search through the source code of websites in order to find cloud resources belonging to a target.
        by Jordan Potti
        @ok_bye_now\n'''
        )   

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
          }

def start(target, depth):
    print("Beginning search for cloud resources in ", target, "\n")
    try:
        start_page = requests.get(target,allow_redirects=True,headers=headers)
    except requests.exceptions.RequestException as e:
        if 'https' in target:
            try:
                start_page = requests.get(target.replace('https','http'),allow_redirects=True,headers=headers)
            except requests.exceptions.RequestException as e:
                print(e)
    links = []
    soup = BeautifulSoup(start_page.text, "lxml")
    for link in soup.findAll('a', attrs={'href':re.compile("^http://")}):
        links.append(link.get('href'))
    for link in soup.findAll('a', attrs={'href':re.compile("^https://")}): 
        links.append(link.get('href'))
    for link in soup.findAll('link', attrs={'href':re.compile("^http://")}): 
        links.append(link.get('href'))
    for link in soup.findAll('link', attrs={'href':re.compile("^https://")}): 
        links.append(link.get('href'))

    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',start_page.text)
    links.extend(urls)
    spider(links,target,depth)

def spider(links,target,depth):
    target_clean = target.replace("https://","")
    target_clean_2 = target_clean.replace("http://","")
    for url in links:
        if (target_clean_2 in url) and url.count("/") < depth+2:
            try:
                page = requests.get(url, allow_redirects=True, headers=headers)
                soup = BeautifulSoup(page.text, "lxml")
                for link in soup.findAll('a', attrs={'href':re.compile("^http://")}):
                    links.append(link.get('href'))
                for link in soup.findAll('a', attrs={'href':re.compile("^https://")}): 
                    links.append(link.get('href'))
                for link in soup.findAll('link', attrs={'href':re.compile("^http://")}): 
                    links.append(link.get('href'))
                for link in soup.findAll('link', attrs={'href':re.compile("^https://")}): 
                    links.append(link.get('href'))
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                if 'https' in target: 
                    try:
                        page = requests.get(target.replace('https','http'),allow_redirects=True,headers=headers)
                        soup = BeautifulSoup(page.text, "lxml")
                        for link in soup.findAll('a', attrs={'href':re.compile("^http://")}):
                            links.append(link.get('href'))
                        for link in soup.findAll('a', attrs={'href':re.compile("^https://")}): 
                            links.append(link.get('href'))
                        for link in soup.findAll('link', attrs={'href':re.compile("^http://")}): 
                            links.append(link.get('href'))
                        for link in soup.findAll('link', attrs={'href':re.compile("^https://")}): 
                            links.append(link.get('href'))
                    except requests.exceptions.RequestException as e:
                        print(e)
            urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',page.text)
            links.extend(urls)
        links = list(set(links))
    parser(links)


def parser(links):
    matches = []
    cloud_matches=['amazonaws.com','digitaloceanspaces.com','windows.net']
    for strings in cloud_matches:
        for link in links:
            if strings in link:
                matches.append(link)
    matches = list(set(matches))
    if len(matches) == 0:
        print("There were no matches!")
    else:
        print("\nThere were ", len(matches), " matches for this search!")
        for match in matches:
            print(match, "\n")

def main():
    global arguments
    global grep_list
    parser = ArgumentParser()
    parser.add_argument("-u", dest="URL", required=False, help="Target Scope") 
    parser.add_argument("-d", dest="depth",type=int, required=False, default=25, help="Max Depth of links Default: 25")
    parser.add_argument("-l", dest="targetlist", required=False, help="Location of text file of Line Delimited targets") 

    if len(sys.argv) == 1:
        parser.error("No arguments given.")
        parser.print_usage
        sys.exit()

#ouput parsed arguments into a usable object
    arguments = parser.parse_args()

    if arguments.targetlist:
        with open (arguments.targetlist, 'r') as target_list:
            for line in target_list:
                if 'http' not in line:
                    line_mod = "https://"+line
                    start(line_mod.rstrip(), arguments.depth)
                else:
                    start(line, arguments.depth)
    else:                
        if 'http' not in arguments.URL:
            line_mod = "https://"+arguments.URL
            start(line_mod.rstrip(), arguments.depth)
        else:
            start(arguments.URL, arguments.depth)
print_banner()
main()
