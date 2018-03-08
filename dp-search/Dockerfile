FROM python:2.7
MAINTAINER David Sullivan "dsullivan0190@gmail.com"
COPY . /dp-search
WORKDIR //dp-search
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver", "-h", "0.0.0.0"]]
