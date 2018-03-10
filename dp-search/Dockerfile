FROM python:2.7
COPY . /dp-search
WORKDIR /dp-search
ENV ELASTICSEARCH_URL elasticsearch:9200
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
# CMD ["manage.py", "runserver", "-h", "0.0.0.0"]
CMD ["manage.py", "runserver"]