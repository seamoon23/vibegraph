import { copyFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';

const root = process.cwd();
const from = resolve(root, 'manifest.json');
const to = resolve(root, 'dist', 'manifest.json');

await mkdir(dirname(to), { recursive: true });
await copyFile(from, to);
