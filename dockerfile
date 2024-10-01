FROM ghcr.io/osgeo/gdal:ubuntu-full-latest

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-dev \
    python3-pip \
    python3-venv \
    gcc \
    g++ \
    libffi-dev \
    libpq-dev \
    libgeos-dev \
    gdal-bin \
    wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    wget http://download.osgeo.org/gdal/2.4.0/gdal-2.4.0.tar.gz && \
    tar -xzf gdal-2.4.0.tar.gz

WORKDIR /app

RUN python3 -m venv /venv
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN /venv/bin/pip install --upgrade pip

COPY requirements.txt /app/

RUN /venv/bin/pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 8000

CMD ["/venv/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]
