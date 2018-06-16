![logo](https://github.com/jordanpotti/CloudScraper/raw/master/media/CloudScraperReadme.png)


#### CloudScraper is a Tool to spider and scrape targets in search of cloud resources. Plug in a URL and it will spider and search the source of spidered pages for strings such as 's3.amazonaws.com', 'windows.net' and 'digitaloceanspaces'. AWS, Azure, Digital Ocean resources are currently supported. 

#### [@ok_bye_now](https://twitter.com/ok_bye_now)

## Pre-Requisites
Non-Standard Python Libraries:

* requests_html
* rfc3987

Created with Python 3.6

## General

This tool was inspired by a recent talk by [Bryce Kunz](https://twitter.com/TweekFawkes). The talk [Blue Cloud of Death: Red Teaming Azure](https://speakerdeck.com/tweekfawkes/blue-cloud-of-death-red-teaming-azure-1) takes us through some of the lesser known common information disclosures outside of the ever common S3 Buckets. 

## Usage:


    usage: CloudScraper.py [-h] [-u URL] [-d DEPTH] [-l TARGETLIST]

    optional arguments:
      -h, --help     show this help message and exit
      -u URL         Target Scope
      -d DEPTH       Max Depth of links Default: 25
      -l TARGETLIST  Location of text file of Line Delimited targets
      -v Verbose     Verbose output

    example: python3 CloudScraper.py -u https://rottentomatoes.com
    
## ToDo

- [ ] Multithread Functionality
- [ ] Add key word customization

## Various:

To add keywords, simply add to the list in the parser function. 

## Contribute

Sharing is caring! Pull requests welcome, things like adding support for more detections, multithreading etc are highly desired :) 

## Why

So Bryce Kunz actually made a tool to do something similar but it used scrapy and I wanted to build something myself that didn't depend on Python2 or any scraping modules such as scrapy. I did end up using BeautifulSoup to parse for href links for spidering only. Hence, CloudScraper was born. The benefit of using raw regex's instead of parsing for href links, is that many times, these are not included in href links, they can be buried in JS or other various locations. CloudScraper grabs the entire page and uses a regex to look for links. This also has its flaws such as grabbing too much or too little but at least we know we are covering our bases :) 
