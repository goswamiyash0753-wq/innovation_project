# innovation_project

## Vercel deployment

- This repository hosts a static site inside the `code/` folder. The entry page is `code/1.html`.
- To deploy automatically to Vercel on each push to `main`, add these repository secrets in GitHub: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.
- A GitHub Actions workflow is provided at `.github/workflows/vercel-deploy.yml` which runs the Vercel Action and deploys the `code/` folder to production.
- Python files are intentionally ignored during deployment via `.vercelignore`.

If you prefer to use the Vercel GitHub app integration instead of GitHub Actions, set the project root to `/` and the framework preset to `Static` and it will detect the `vercel.json` routing.
