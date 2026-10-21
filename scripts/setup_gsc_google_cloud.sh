#!/usr/bin/env bash
# One-time Google Cloud setup for TPP Search Console automation.
# Run inside Google Cloud Shell as a project admin. No permanent keys.
set -Eeuo pipefail
PROJECT="abiding-envoy-512322-p0"
REPO="TPGmail/tienphat-website"
POOL="tpp-github"
PROVIDER="tpp-main"
SA_ID="tpp-gsc-sync"
SA="$SA_ID@$PROJECT.iam.gserviceaccount.com"

command -v gcloud >/dev/null || { echo "gcloud CLI is required" >&2; exit 1; }
echo "Checking access to $PROJECT..."
NUMBER="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
[[ -n "$NUMBER" ]] || { echo "Cannot determine project number" >&2; exit 1; }

echo "Enabling Cloud APIs..."
gcloud services enable iam.googleapis.com iamcredentials.googleapis.com sts.googleapis.com searchconsole.googleapis.com --project="$PROJECT" --quiet

if gcloud iam service-accounts describe "$SA" --project="$PROJECT" >/dev/null 2>&1; then
  echo "Existing service account: $SA"
else
  gcloud iam service-accounts create "$SA_ID" --project="$PROJECT" \
    --display-name="TPP Search Console automation" --quiet
fi

if gcloud iam workload-identity-pools describe "$POOL" --location=global --project="$PROJECT" >/dev/null 2>&1; then
  echo "Existing identity pool: $POOL"
else
  gcloud iam workload-identity-pools create "$POOL" --project="$PROJECT" --location=global \
    --display-name="TPP GitHub Actions" --quiet
fi

if gcloud iam workload-identity-pools providers describe "$PROVIDER" \
  --project="$PROJECT" --location=global --workload-identity-pool="$POOL" >/dev/null 2>&1; then
  echo "Existing provider: $PROVIDER. Review condition/mapping before using."
else
  gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" \
    --project="$PROJECT" --location=global --workload-identity-pool="$POOL" \
    --issuer-uri="https://token.actions.githubusercontent.com" \
    --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
    --attribute-condition="assertion.repository == '$REPO' && assertion.ref == 'refs/heads/main'" \
    --quiet
fi

MEMBER="principalSet://iam.googleapis.com/projects/$NUMBER/locations/global/workloadIdentityPools/$POOL/attribute.repository/$REPO"
gcloud iam service-accounts add-iam-policy-binding "$SA" --project="$PROJECT" \
  --member="$MEMBER" --role="roles/iam.workloadIdentityUser" --quiet >/dev/null

echo
echo "Google Cloud portion complete for project: $PROJECT"
echo "Add this service account as a FULL user of Search Console sc-domain:tienphat.org:"
echo "$SA"
echo
echo "In GitHub repository $REPO go to Settings > Secrets and variables > Actions > Variables."
echo "Create two non-secret REPOSITORY VARIABLES:"
echo "GSC_WIF_PROVIDER = projects/$NUMBER/locations/global/workloadIdentityPools/$POOL/providers/$PROVIDER"
echo "GSC_SERVICE_ACCOUNT = $SA"
echo
echo "Then open GitHub Actions > TPP Technical SEO and Search Console > Run workflow."
echo "Do not paste Google tokens, downloaded JSON keys, or passwords into ChatGPT."
