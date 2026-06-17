# Deploying Ledgr

A live demo link is the single biggest thing you can add to make this repo land
interviews — reviewers click it before they read code. Everything here uses free
tiers.

## Recommended split

- **Database + backend** → [Render](https://render.com) or [Railway](https://railway.app)
- **Frontend** → [Vercel](https://vercel.com) or [Netlify](https://netlify.com)

Both halves are already containerised and config-driven, so deployment is mostly
setting environment variables.

## Backend (Render example)

1. New → **PostgreSQL** instance. Copy its **Internal Database URL**.
2. New → **Web Service**, point it at this repo, root directory `backend`,
   environment **Docker** (it'll use `backend/Dockerfile`). The image already
   runs `alembic upgrade head` on start.
3. Set environment variables:

   | Key | Value |
   |---|---|
   | `APP_NAME` | `Ledgr` |
   | `APP_VERSION` | `0.1.0` |
   | `DATABASE_URL` | the Postgres URL, with the scheme `postgresql+asyncpg://...` |
   | `LOG_LEVEL` | `INFO` |
   | `JWT_SECRET_KEY` | a long random string |
   | `JWT_ALGORITHM` | `HS256` |
   | `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` |
   | `CORS_ORIGINS` | your frontend URL, e.g. `https://ledgr.vercel.app` |

   > Render's Postgres URL starts with `postgres://`; rewrite it to
   > `postgresql+asyncpg://` for this app.

4. Deploy. Health check path: `/healthz`.

## Frontend (Vercel example)

1. Import the repo, set the **root directory** to `frontend`.
2. Framework preset: **Vite**. Build command `npm run build`, output `dist`.
3. Environment variable:

   | Key | Value |
   |---|---|
   | `VITE_API_BASE_URL` | `https://<your-backend>.onrender.com/api/v1` |

4. Deploy, then add the resulting URL to the backend's `CORS_ORIGINS` and
   redeploy the backend.

## After deploying

- Put the live URL at the top of the README and your CV.
- Seed a demo merchant so reviewers can log in without signing up, or just let
  them sign up — it takes 10 seconds.

## Notes

- The in-process webhook dispatcher and background jobs run inside the web
  service; on free tiers that sleep, they pause while the service is idle. For a
  always-on setup, run them as a separate worker process.
- Never commit real secrets. `JWT_SECRET_KEY` and the database URL live only in
  the platform's environment settings.
