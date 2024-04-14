FROM python:3



# Give execution rights on the cron job


# Apply cron job


# Create the log file to be able to run tail



# Run the command on container startup


ADD requirements.txt /
RUN pip install -r requirements.txt
COPY authentication/* /authentication/
COPY elektrum_ha/* /elektrum_ha/
ADD web-api.py /
ADD .env /
RUN chmod 755 ./web-api.py
CMD [ "python", "./web-api.py" ]
# CMD ["print" ,"Hello Docker!" ]