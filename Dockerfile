FROM python:3.7-stretch as build-stage

ARG GOOGLE_CREDENTIALS_DECRYPT

ENV GOOGLE_CREDENTIALS_DECRYPT ${GOOGLE_CREDENTIALS_DECRYPT}

WORKDIR /app

COPY . .

RUN if [ -f business/oauth/credentials.dat ]; then \
        echo 'credentials exist, skipping'; \
    else \
        echo 'decrypting Google credentials' && \
        ./oauth_decrypt.sh; \
    fi

FROM python:3.7-stretch as production-stage

WORKDIR /app

ENV PYTHONPATH /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir business

COPY --from=build-stage /app/business business

RUN if [ -d business/logs ]; then \
      echo 'logs directory exists, skipping'; \
    else \
        mkdir logs; \
    fi

CMD ["python", "business/sync/entrypoint.py"]
