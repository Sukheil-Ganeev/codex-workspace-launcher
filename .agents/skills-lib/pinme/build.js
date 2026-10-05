require('dotenv').config();
const esbuild = require('esbuild');

const define = {};
for (const key in process.env) {
  define[`process.env.${key}`] = JSON.stringify(process.env[key]);
}

define['process.env.IPFS_PREVIEW_URL'] = JSON.stringify(process.env.IPFS_PREVIEW_URL);
define['process.env.SECRET_KEY'] = JSON.stringify(process.env.SECRET_KEY);

esbuild.build({
  entryPoints: ['bin/index.ts'],
  outfile: 'dist/index.js',
  bundle: true,
  platform: 'node',
  target: 'node14',
  format: 'cjs',
  external: Object.keys(require('./package.json').dependencies || {}).filter(dep => dep !== 'axios'),
  banner: { js: '#!/usr/bin/env node' },
  logLevel: 'info',
  define,
}).catch(() => process.exit(1)); 