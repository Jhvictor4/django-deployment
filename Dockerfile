FROM python:3.8

RUN mkdir /code

WORKDIR /code

ADD ./assignment2/ /code/

RUN pip install -r requirements.txt

#CMD ["source", "venv/bin/activate"]
#
#CMD ["gunicorn", "waffle_backend.wsgi:application", "--bind", "0:8000"]
#
#EXPOSE 8000