#!/bin/bash

# Path to the template file and the destination file
TEMPLATE_FILE="/opt/keycloak/data/templates/SOF-realm-template.json"
REALM_FILE="/opt/keycloak/data/import/SOF-realm.json"

mkdir -p /opt/keycloak/data/import

echo "Replacing placeholders in realm configuration file..."

SUPERUSER_CREATED_TIMESTAMP=$(date +%s%3N)

# Replace placeholders with environment variables
sed -e "s|__SUPERUSER_EMAIL__|${SUPERUSER_EMAIL}|g" \
    -e "s|__SUPERUSER_CREATED_TIMESTAMP__|${SUPERUSER_CREATED_TIMESTAMP}|g" \
    -e "s|__EMAIL_SMTP_HOST__|${EMAIL_SMTP_HOST}|g" \
    -e "s|__EMAIL_SMTP_PORT__|${EMAIL_SMTP_PORT}|g" \
    -e "s|__EMAIL_SMTP_USERNAME__|${EMAIL_SMTP_USERNAME}|g" \
    -e "s|__EMAIL_SMTP_PASSWORD__|${EMAIL_SMTP_PASSWORD}|g" \
    $TEMPLATE_FILE > $REALM_FILE


## Start Keycloak with the modified realm configuration
exec /opt/keycloak/bin/kc.sh "$@"
