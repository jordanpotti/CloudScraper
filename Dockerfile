FROM python

WORKDIR /usr/src/CloudScraper

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY ./ ./
ENTRYPOINT ["python3", "/usr/src/CloudScraper/CloudScraper.py"]

