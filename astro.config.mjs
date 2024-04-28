import { defineConfig } from 'astro/config';

import mdx from "@astrojs/mdx";

// https://astro.build/config
export default defineConfig({
  site: 'https://raphben69.github.io',
  base: 'APE',
  integrations: [mdx()]
});