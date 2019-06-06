FROM python:3

LABEL maintainer="yanzhao3@illinois.edu" author="Yan Zhao"

WORKDIR /app
RUN apt-get update && apt-get install -y libldap2-dev libsasl2-dev libssl-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt && \
  pip install gunicorn 

COPY transformations/ /app/transformations/

CMD [ "gunicorn", "-w 4", "-b 0.0.0.0:5000", "transformations:create_app()"]
