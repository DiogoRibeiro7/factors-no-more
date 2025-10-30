
#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/setup_repo.sh your-org factors-no-more
ORG="${1:-your-org}"
REPO="${2:-factors-no-more}"

# Create repo (private) if it doesn't exist
gh repo view "$ORG/$REPO" >/dev/null 2>&1 || gh repo create "$ORG/$REPO" --private --source=. --push

# Default branch main
git branch -M main
git push -u origin main

# Protect main
gh api --method PUT repos/$ORG/$REPO/branches/main/protection   -H "Accept: application/vnd.github+json"   -f required_status_checks[strict]=true   -f required_status_checks[contexts][]=ruff   -f required_status_checks[contexts][]=mypy   -f required_status_checks[contexts][]=pytest   -F enforce_admins=true   -F required_pull_request_reviews[dismiss_stale_reviews]=true   -F required_pull_request_reviews[required_approving_review_count]=1   -F restrictions=

# Create develop and push
git checkout -b develop
git push -u origin develop

# Protect develop (looser)
gh api --method PUT repos/$ORG/$REPO/branches/develop/protection   -H "Accept: application/vnd.github+json"   -f required_status_checks[strict]=false   -F enforce_admins=false   -F required_pull_request_reviews[required_approving_review_count]=0   -F restrictions=

echo "Branch protections set for main and develop."
