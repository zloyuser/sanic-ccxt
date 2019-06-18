FROM python:3.7-alpine

RUN apk update
RUN apk add wget build-base ca-certificates openssl-dev libffi-dev

RUN pip install --upgrade pip

# Numpy
RUN pip install cython
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN pip install numpy

# TA-Lib
RUN wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz && \
  tar -xvzf ta-lib-0.4.0-src.tar.gz && \
  cd ta-lib/ && \
  ./configure --prefix=/usr && \
  make && \
  make install

RUN mkdir /app

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080 8443

ENTRYPOINT ["python", "main.py", "--port", "8080"]
CMD []
