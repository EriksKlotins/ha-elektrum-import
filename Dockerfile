FROM python:3


ADD requirements.txt /
RUN pip install -r requirements.txt
COPY authentication/* /authentication/
COPY elektrum_ha/* /elektrum_ha/
ADD web-api.py /
ADD .env /
RUN chmod 755 ./web-api.py
CMD [ "python", "./web-api.py" ]
# CMD ["print" ,"Hello Docker!" ] to
