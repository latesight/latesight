#!/usr/bin/env sh

set -eu

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1/health}"
HEALTH_HOST="${HEALTH_HOST:-dict.latesight.com}"
HEALTH_RETRIES="${HEALTH_RETRIES:-20}"
HEALTH_INTERVAL="${HEALTH_INTERVAL:-3}"
ROLLBACK_ON_FAILURE="${ROLLBACK_ON_FAILURE:-1}"
PREVIOUS_COMMIT="${PREVIOUS_COMMIT:-}"
TARGET_COMMIT="${TARGET_COMMIT:-}"

log() {
  printf '%s\n' "$1"
}

health_check() {
  ATTEMPT=1
  while [ "$ATTEMPT" -le "$HEALTH_RETRIES" ]; do
    if curl -fsS -H "Host: ${HEALTH_HOST}" "$HEALTH_URL" >/dev/null 2>&1; then
      log "[RepoDeploy.run] health check passed attempt=${ATTEMPT}"
      return 0
    fi

    log "[RepoDeploy.run] health check pending attempt=${ATTEMPT}/${HEALTH_RETRIES}"
    ATTEMPT=$((ATTEMPT + 1))
    sleep "$HEALTH_INTERVAL"
  done

  return 1
}

cleanup_legacy_containers() {
  docker rm -f xhome >/dev/null 2>&1 || true
}

cleanup_build_artifacts() {
  log "[RepoDeploy.run] cleaning previous build artifacts"
  rm -rf \
    "${PROJECT_DIR}/apps/home/.next" \
    "${PROJECT_DIR}/apps/dict/.next" \
    "${PROJECT_DIR}/.turbo"
}

prebuild() {
  cleanup_build_artifacts

  log "[RepoDeploy.run] pre-building packages on host filesystem"
  docker run --rm --security-opt seccomp=unconfined \
    -v "${PROJECT_DIR}":/app \
    -w /app \
    node:22-alpine \
    sh -c "npm install -g pnpm@10.0.0 && pnpm install --frozen-lockfile && pnpm build"
  log "[RepoDeploy.run] pre-build complete"
}

start_stack() {
  log "[RepoDeploy.run] stopping existing containers"
  docker compose down --remove-orphans || true
  cleanup_legacy_containers

  log "[RepoDeploy.run] rebuilding and starting containers"
  docker compose up -d --build --remove-orphans

  log "[RepoDeploy.run] current container status"
  docker compose ps
}

rollback() {
  if [ "$ROLLBACK_ON_FAILURE" != "1" ]; then
    log "[RepoDeploy.run] rollback disabled" >&2
    return 1
  fi

  if [ -z "$PREVIOUS_COMMIT" ]; then
    log "[RepoDeploy.run] rollback skipped: no previous commit recorded" >&2
    return 1
  fi

  log "[RepoDeploy.run] rolling back to commit=${PREVIOUS_COMMIT}"
  git checkout --detach "$PREVIOUS_COMMIT"
  prebuild
  start_stack

  if health_check; then
    log "[RepoDeploy.run] rollback recovered service"
  else
    log "[RepoDeploy.run] rollback health check failed" >&2
  fi
}

log "[RepoDeploy.run] project_dir=${PROJECT_DIR} target_commit=${TARGET_COMMIT:-unknown}"
log "[RepoDeploy.run] health_url=${HEALTH_URL} health_host=${HEALTH_HOST} retries=${HEALTH_RETRIES} interval=${HEALTH_INTERVAL} rollback=${ROLLBACK_ON_FAILURE}"

cd "$PROJECT_DIR"

prebuild
start_stack

log "[RepoDeploy.run] waiting for health endpoint"
if health_check; then
  log "[RepoDeploy.run] deployment finished commit=${TARGET_COMMIT:-unknown}"
  exit 0
fi

log "[RepoDeploy.run] health check failed; recent logs follow" >&2
docker compose logs --tail=80 api proxy dict home postgres valkey >&2 || true
rollback || true
exit 1
