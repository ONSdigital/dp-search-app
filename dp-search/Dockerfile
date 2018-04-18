FROM python:2.7
COPY . /dp-search
WORKDIR /dp-search
RUN tar -xvf models.tar.bz2
RUN pip install --upgrade pip
RUN pip install Cython pybind11
RUN cd lib/fastText/ && python setup.py install
RUN pip install -r requirements.txt
ENV FLASK_CONFIG production
#ENTRYPOINT ["python"]
#CMD ["manage.py", "runserver"]
CMD ["./run_gunicorn.sh"]