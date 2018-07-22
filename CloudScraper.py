import requests
import re
from argparse import ArgumentParser
import sys
import rfc3987

grep_list = None

arguments = None
links_done = set()

def print_banner():
    print('''\nDescription: 
        CloudScraper is a tool to search through the source code of websites in order to find cloud resources belonging to a target.
        by Jordan Potti
        @ok_bye_now\n'''
          )


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
}


def check_valid_url(url):
    try:
        rfc3987.parse(url)
        return True
    except ValueError:
        return False


def get_links_from_html(html):
    links = []
    urls = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', html)
    links.extend(filter(check_valid_url, urls))  # filter the ones that don't compile with the checker function
    return set(links)


def start(target, depth):
    global links_done
    print("Beginning search for cloud resources in ", target, "\n")
    try:
        start_page = requests.get(target, allow_redirects=True, headers=headers)
    except requests.exceptions.RequestException as e:
        if 'https' in target:
            try:
                start_page = requests.get(target.replace('https', 'http'), allow_redirects=True, headers=headers)
            except requests.exceptions.RequestException as e:
                print(e)

    links = get_links_from_html(start_page.text)
    links_done = links_done.union(links)
    parser(links)
    spider(links, target, depth)


def spider(links, target, depth):
    global links_done
    target_clean = re.sub('^https?://', "", target)
    for link in links:
        if target_clean in link and link.count("/") < depth + 2:
            page = requests.get(link, allow_redirects=True, headers=headers).text
            more_links = get_links_from_html(page)
            more_links.difference_update(links_done)
            links_done=links_done.union(more_links)
            if len(more_links) > 0:
                parser(links)
                spider(more_links, target, depth)


def parser(links):
    matches = []
    cloud_matches = ['amazonaws.com', 'digitaloceanspaces.com', 'windows.net']
    for strings in cloud_matches:
        for link in links:
            if strings in link:
                matches.append(link)
    matches = list(set(matches))
    if len(matches) > 0:
        for match in matches:
            print(match, "\n")


def main():
    global arguments
    parser = ArgumentParser()
    parser.add_argument("-u", dest="URL", required=False, help="Target Scope")
    parser.add_argument("-d", dest="depth", type=int, required=False, default=25, help="Max Depth of links Default: 25")
    parser.add_argument("-l", dest="targetlist", required=False, help="Location of text file of Line Delimited targets")

    if len(sys.argv) == 1:
        parser.error("No arguments given.")
        parser.print_usage
        sys.exit()

    # ouput parsed arguments into a usable object
    arguments = parser.parse_args()

    if arguments.targetlist:
        with open(arguments.targetlist, 'r') as target_list:
            for line in target_list:
                if line.startswith('http'):
                    line_mod = "https://" + line
                    start(line_mod.rstrip(), arguments.depth)
                else:
                    start(line, arguments.depth)
    else:
        if not arguments.URL.startswith('http'):
            line_mod = "https://" + arguments.URL
            start(line_mod.rstrip(), arguments.depth)
        else:
            start(arguments.URL, arguments.depth)


print_banner()
main()
