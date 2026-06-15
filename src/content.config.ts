import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const schema = z.object({
	title: z.string(),
	description: z.string(),
	publishDate: z.coerce.date(),
	tags: z.array(z.string()),
	img: z.string(),
	img_alt: z.string().optional(),
});

const Year2024 = defineCollection({
	loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/Year2024' }),
	schema,
});

const Year2025 = defineCollection({
	loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/Year2025' }),
	schema,
});

export const collections = { Year2024, Year2025 };
