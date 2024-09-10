import { defineConfig } from 'astro/config';

import mdx from "@astrojs/mdx";

// https://astro.build/config
export default defineConfig({
  site: 'https://apesteanne.fr',
  base: 'APE',
  integrations: [mdx()],
  redirects: {
    '/404': '/index'
    }
});