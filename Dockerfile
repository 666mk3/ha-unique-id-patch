ARG BUILD_FROM
FROM $BUILD_FROM

# Install requirements for add-on
RUN apk add --no-cache python3 py3-pip

WORKDIR /app
COPY app/ /app/
COPY requirements.txt /app/

# Python 3.12+ (Alpine 3.19+) requires --break-system-packages or a venv
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt

# Copy startup script
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]
