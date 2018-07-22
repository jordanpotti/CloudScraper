import requests
import re
from argparse import ArgumentParser
import sys
import rfc3987
import threading
import queue

links_done = set()
q = queue.Queue()


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


def make_request_and_queue(link, target, depth, verbose):
    global links_done
    target_clean = re.sub('^https?://', "", target)
    if target_clean in link and link.count("/") < depth + 2:
        page = requests.get(link, allow_redirects=True, headers=headers).text
        if verbose:
            print("GETting %s" %link)
        # Update the history of links requested
        links_done.add(link)
        links_to_spider = get_links_from_html(page)
        # We make sure to remove duplicates so we don't make requests twice to the same endpoint
        links_to_spider.difference_update(links_done)

        for url in links_to_spider:
            q.put({'target': target_clean, 'link': url})
        if len(links_to_spider) > 0:
            check_cloud_in_links(links_to_spider)


def check_cloud_in_links(links):
    matches = []
    cloud_matches = ['amazonaws.com', 'digitaloceanspaces.com', 'windows.net']
    for cloud in cloud_matches:
        for link in links:
            if cloud in link:
                matches.append(link)
    matches = list(set(matches))
    if len(matches) > 0:
        for match in matches:
            print(match, "\n")


def worker(depth, verbose):
    while True:
        item = q.get()
        if item is None:
            break
        make_request_and_queue(item['link'], item['target'], depth, verbose)
        q.task_done()


def main():
    global arguments
    parser = ArgumentParser()

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-u", dest="URL", help="Target Scope")
    group.add_argument("-l", dest="targetlist", help="Location of text file of Line Delimited targets")

    parser.add_argument("-d", dest="depth", type=int, required=False, default=25, help="Max Depth of links Default: 25")
    parser.add_argument("-t", dest="threads", type=int, required=False, default=2, help="Number of threads: 2")
    parser.add_argument("-v", dest="verbose", required=False, action='store_true', help="Verbose")

    if len(sys.argv) == 1:
        parser.error("No arguments given.")

    # ouput parsed arguments into a usable object
    arguments = parser.parse_args()

    targets = []
    if arguments.targetlist:
        with open(arguments.targetlist, 'r') as target_list:
            for target in target_list:
                if target.startswith('http'):
                    target = "https://" + target.strip()
                targets.append(target)
    else:
        target = arguments.URL.strip()
        if not arguments.URL.startswith('http'):
            target = "https://" + target
        targets.append(target)

    number_of_threads = arguments.threads
    depth = arguments.depth
    verbose = arguments.verbose

    # spawn the threads
    for i in range(0, number_of_threads):
        t = threading.Thread(target=worker, args=(depth,verbose))
        t.start()

    # queue the targets
    for target in targets:
        q.put({'target': target, 'link': target})

    # Wait for all jobs get done
    q.join()

    for i in range(0, arguments.threads):
        # put a NoneType so the blocking thread get free and exit
        q.put(None)


print_banner()
main()
