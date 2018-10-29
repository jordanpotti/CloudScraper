FROM python:3-slim 

LABEL name CloudScraper
LABEL src "https://github.com/jordanpotti/CloudScraper"
LABEL creator jordanpotti
LABEL dockerfile_maintenance khast3x
LABEL desc "CloudScraper: Tool to enumerate targets in search of cloud resources. S3 Buckets, Azure Blobs, Digital Ocean Storage Space"

RUN apt-get update && apt-get install -y git \
    && pip install lxml \
    && git clone https://github.com/jordanpotti/CloudScraper.git
WORKDIR CloudScraper
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "CloudScraper.py"]
CMD ["-h"]