FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc build-essential openssl ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove gcc build-essential openssl ca-certificates

COPY . .

EXPOSE 80 443

ENTRYPOINT ["python", "main.py"]
CMD []
