# Census Atlas website

The Census Atlas source lives in [quant-shop/census/apps/census-atlas](https://github.com/quant-shop/census/tree/main/apps/census-atlas). This repository publishes that app at [quant-shop.github.io/census-dashboard](https://quant-shop.github.io/census-dashboard/).

The GitHub Pages workflow checks out the source folder, runs `npm ci && npm run check`, and deploys its `dist/` directory. It runs when this repository's `main` branch changes, when started manually, and every six hours to pick up changes from `quant-shop/census`.

To enable the site, merge the deployment pull request and select **GitHub Actions** in this repository's **Settings → Pages → Build and deployment → Source**. Future app changes belong in `quant-shop/census/apps/census-atlas`.
