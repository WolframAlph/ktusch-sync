FROM python:3.7-alpine3.11 as build-stage

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

FROM python:3.7-alpine3.11 as production-stage

WORKDIR /app

ENV PYTHONPATH /app

COPY requirements.txt .

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install -r requirements.txt

RUN mkdir business

COPY --from=build-stage /app/business business

RUN if [ -d business/logs ]; then \
      echo 'logs directory exists, skipping'; \
    else \
        mkdir business/logs; \
    fi

EXPOSE 5000

CMD ["python", "business/rest/api.py"]
