FROM python:2.7
COPY . /dp-search
WORKDIR /dp-search
RUN pip install --upgrade pip
RUN pip install Cython pybind11
RUN cd lib/fastText/ && python setup.py install
RUN pip install -r requirements.txt
ENV FLASK_CONFIG development
ENTRYPOINT ["python"]
CMD ["manage.py", "runserver"]