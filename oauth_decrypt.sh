#!/bin/bash

gpg --quiet --batch --yes --decrypt --passphrase="$GOOGLE_CREDENTIALS_DECRYPT" \
--output business/oauth/credentials.dat business/oauth/credentials.dat.gpg
