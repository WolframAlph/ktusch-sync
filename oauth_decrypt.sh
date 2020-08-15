#!/bin/bash

gpg --quiet --batch --yes --decrypt --passphrase="$GOOGLE_CREDENTIALS_DECRYPT" \
--output oauth/credentials.dat oauth/credentials.dat.gpg
