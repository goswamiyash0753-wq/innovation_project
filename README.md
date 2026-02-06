<div align="center">

# 🚀 innovation_project

**A minimal static HTML & CSS site**

[![Vercel](https://img.shields.io/badge/deploy-vercel-000?style=for-the-badge&logo=vercel&logoColor=white)](https://innovation-lake-nine.vercel.app/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?style=for-the-badge)](LICENSE)

</div>

---

## About

- A minimal static website stored in the `code/` folder. The site entry page is [code/1.html](code/1.html).
- **Live demo:** https://innovation-lake-nine.vercel.app/

## Table of Contents
- [Features](#features)
- [Project structure](#project-structure)
- [Preview locally](#preview-locally)
- [Deployment](#deployment)
- [CI / GitHub Actions](#ci--github-actions)
- [Contributing](#contributing)
- [License](#license)

## Features
- Static HTML/CSS site — no backend required.
- Vercel-ready configuration to route `/` to the site entry page.

## Project structure
- [code/](code/) — site files (HTML, CSS, assets). Starting page: [code/1.html](code/1.html)
- [vercel.json](vercel.json) — Vercel routing and static build settings
- [.vercelignore](.vercelignore) — excludes Python and dev files from deployment
- [.github/workflows/vercel-deploy.yml](.github/workflows/vercel-deploy.yml) — GitHub Actions workflow for automatic deploys
- [LICENSE](LICENSE) — project license

## Preview locally
To preview the static site locally you can use a simple HTTP server. Example using Python 3:

```bash
cd code
python3 -m http.server 8000
# open http://localhost:8000/1.html
```

Alternatively, use any static server (Node http-server, live-server, etc.).

## Deployment
The repository is configured for Vercel deployments. The root path `/` is routed to [code/1.html](code/1.html) via [vercel.json](vercel.json).

Quick setup (Vercel + GitHub Actions):
1. Create a Vercel project and link it to this repository, or create the project on Vercel and copy the project ID and org ID.
2. Add these repository secrets in GitHub: `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID`.
3. Push to `main` — the workflow `.github/workflows/vercel-deploy.yml` will run and deploy the `code/` folder.

If you prefer the Vercel GitHub App integration, install it and set the project root appropriately (Static preset).

## CI / GitHub Actions
The included workflow [/.github/workflows/vercel-deploy.yml](.github/workflows/vercel-deploy.yml) uses the amondnet/vercel-action to perform a production deploy on pushes to `main`. Ensure GitHub secrets are set as described above.

## Contributing
- Use Issues for bug reports and feature requests.
- For code changes, open a focused pull request describing the change.

## License
This project is released under the MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
  <p><strong>Thank you for visiting! 🚀</strong></p>
</div>


