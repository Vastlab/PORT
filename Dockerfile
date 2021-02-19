FROM tiangolo/meinheld-gunicorn-flask:python3.7
COPY ./app /app
RUN pip install numpy flask
