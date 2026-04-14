#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_FILE="${APP_FILE:-main.py}"
ADDRESS="${STREAMLIT_ADDRESS:-0.0.0.0}"
PORT="${STREAMLIT_PORT:-443}"
SSL_CN="${STREAMLIT_SSL_CN:-localhost}"
CERT_DIR="${ROOT_DIR}/.streamlit/certs"
CERT_FILE="${STREAMLIT_SSL_CERT_FILE:-${CERT_DIR}/streamlit-selfsigned.crt}"
KEY_FILE="${STREAMLIT_SSL_KEY_FILE:-${CERT_DIR}/streamlit-selfsigned.key}"

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

generate_self_signed_cert() {
  mkdir -p "${CERT_DIR}"
  openssl req \
    -x509 \
    -nodes \
    -days 365 \
    -newkey rsa:2048 \
    -keyout "${KEY_FILE}" \
    -out "${CERT_FILE}" \
    -subj "/CN=${SSL_CN}" >/dev/null 2>&1
  chmod 600 "${KEY_FILE}"
}

require_command streamlit
require_command openssl

if [[ ! -f "${CERT_FILE}" || ! -f "${KEY_FILE}" ]]; then
  generate_self_signed_cert
fi

if (( PORT < 1024 )) && [[ "${EUID}" -ne 0 ]]; then
  echo "Re-running with sudo so Streamlit can bind to port ${PORT}."
  exec sudo -E bash "$0" "$@"
fi

exec streamlit run "${ROOT_DIR}/${APP_FILE}" \
  --server.address "${ADDRESS}" \
  --server.port "${PORT}" \
  --server.headless true \
  --server.sslCertFile "${CERT_FILE}" \
  --server.sslKeyFile "${KEY_FILE}"
