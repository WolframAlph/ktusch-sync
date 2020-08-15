FROM python:3.7-stretch

ARG GOOGLE_CREDENTIALS_DECRYPT

WORKDIR /app

ENV GOOGLE_CREDENTIALS_DECRYPT ${GOOGLE_CREDENTIALS_DECRYPT}

ENV PYTHONPATH="/app"

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN if [ -d logs ]; then \
      echo 'logs directory exists, skipping'; \
    else \
        mkdir logs; \
    fi

RUN if [ -f oauth/credentials.dat ]; then \
        echo 'credentials exist, skipping'; \
    else \
        echo 'decrypting Google credentials' && \
        ./oauth_decrypt.sh; \
    fi

CMD ["python", "sync/entrypoint.py"]
