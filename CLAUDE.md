# smoothiemixer

FastAPI backend (`backend/`) + React/Vite frontend (`frontend/`). SQLite DB, single Docker image, deployed to a Raspberry Pi.

## Deploy

Production: Raspberry Pi at `192.168.1.31` (`raspberrypi.local`), port `8080`, app dir `/home/pi/smoothiemixer/`. SSH user `pi`. Docker on that Pi is managed via Portainer at `192.168.1.40`.

Build locally, not on the Pi — the Pi's SD card and CPU make on-device builds slow, and both the Mac (Apple Silicon) and the Pi are arm64, so no cross-compile is needed:

1. `rsync -av --exclude '.venv' --exclude 'node_modules' --exclude 'dist' --exclude '__pycache__' --exclude '.git' --exclude '*.db' ./ pi@192.168.1.31:/home/pi/smoothiemixer/`
2. `colima start` (no Docker Desktop on this Mac; colima runs the daemon)
3. `docker build --platform linux/arm64 -t smoothiemixer-smoothiemixer:latest .`
4. `docker save smoothiemixer-smoothiemixer:latest | gzip > /tmp/smoothiemixer.tar.gz`, `scp` to the Pi, then on the Pi: `gunzip -c /tmp/smoothiemixer.tar.gz | docker load`
5. On the Pi: `docker compose up -d --no-build`
6. Clean up the tarball and `docker image prune -f` on the Pi

If `docker build` fails on `docker-credential-osxkeychain: executable file not found`, use a scratch `DOCKER_CONFIG` dir with `{"auths": {}}` rather than editing `~/.docker/config.json`.

## Exposing new routes/subdomains

Traefik config lives outside this repo at `/Volumes/storage/dockerconfigs/traefik/config/services.yml` (runs on 192.168.1.40, same host as Portainer). That directory is a network share, so traefik's file-provider `watch: true` never picks up edits (inotify doesn't fire over NFS/SMB) — after editing `services.yml`, you must `docker restart traefik` on 192.168.1.40.

## Schema changes to `ingredients`

The production DB already had rows before some columns (e.g. macros) existed. `seed()` only inserts starter rows into an empty table, so `ALTER TABLE ... ADD COLUMN` alone leaves pre-existing rows stuck at the column default forever. When adding a new ingredient attribute, always pair the migration with a backfill step that matches existing rows by name against `STARTER_INGREDIENTS` and only overwrites rows still at the post-migration default (see `backfill_macros()` in `backend/seed.py` for the pattern). Verify against a real snapshot of the Pi's DB, not just a fresh dev DB — pull one with `docker cp <container>:/data/smoothiemixer.db /tmp/x.db` on the Pi, then `scp` it down.
