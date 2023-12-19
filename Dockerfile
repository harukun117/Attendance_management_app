FROM python:3.9.16
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD . /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN chmod a+x build.sh
ENTRYPOINT [ "bash", "./build.sh" ]
EXPOSE 8000
CMD [ "gunicorn", "config.wsgi:application" ]
