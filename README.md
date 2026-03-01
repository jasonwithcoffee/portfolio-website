# Landing page demo

This repository contains a minimal static landing page under the `www/` folder. The included `app.yaml` and `cloudbuild.yaml` are configured to deploy the site to Google App Engine using Cloud Build.

Quick deploy steps (manual):

1. Install and authenticate the Google Cloud SDK.
2. Set your project: `gcloud config set project YOUR_PROJECT_ID`
3. Deploy: `gcloud app deploy`

CI via Cloud Build (GitHub):

- Create a Cloud Build trigger in the Google Cloud Console that connects to your GitHub repository and triggers on pushes to the branch you want to deploy.
- The existing `cloudbuild.yaml` runs `gcloud app deploy` and will deploy the App Engine app.

Notes:
- The site is static and served from `www/` as configured in `app.yaml`.
- If you prefer Cloud Functions/Cloud Run instead of App Engine, I can scaffold that.
