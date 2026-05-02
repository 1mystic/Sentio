## AI Context Snapshot

Date: 2025-11-18

Purpose: quick context file for AI copilots to understand recent work and next steps.

---

**Project**: Veramind — frontend migrated from Nuxt 3 -> Vite + Vue 3 (in progress).

**High-level summary**:
- Migrated project away from Nuxt-specific runtime to a Vite + Vue 3 setup.
- Added a Vite entry (`index.html` + `src/main.js`), created `src/router/index.js`, and replaced many `NuxtLink`/`NuxtPage` usages with `RouterLink` and `<router-view/>`.
- Rewrote Supabase client to use `import.meta.env.VITE_*` vars and made server-side Gemini handler portable for serverless/Node.
- Updated `package.json` scripts to use Vite and installed `vue`, `vue-router@4`, and `@supabase/supabase-js`.

**What changed (key files)**:
- `package.json` — Vite scripts and dependencies
- `index.html` — Vite HTML entry
- `src/main.js` — createApp + router mount
- `src/router/index.js` — routes mapping pages
- `src/app.vue` — replaced NuxtPage with `<router-view/>`
- `src/integrations/supabase/client.js` — uses `import.meta.env.VITE_SUPABASE_*`
- `src/server/api/gemini/chat.js` — portable server handler (reads `process.env` for secrets)
- Many `src/pages/*.vue` and `src/components/*` — replaced `~` alias imports and `NuxtLink` usage

**Current status**:
- App is runnable with Vite. Dev server starts (http://localhost:5173/) after installing missing deps.
- Remaining work: finish wiring router in a few files, ensure all alias imports are resolved (most have been converted), convert any additional server endpoints to target platform handlers, add optional `vite.config.js` aliases if desired.

**Important environment variables** (local development):
- `VITE_SUPABASE_URL` — your Supabase project URL (client-exposed)
- `VITE_SUPABASE_ANON_KEY` — Supabase anonymous key (client-exposed)
- `GEMINI_API_KEY` or `VITE_GEMINI_API_KEY` — server-side only; keep secret and provide via serverless platform settings

Note: Any `VITE_` prefixed vars are safe to expose client-side. Keep real secrets in server-only envs.

**Common commands**:
```
npm install
npm run dev       # start Vite dev server
npm run build     # build for production
npm run preview   # preview production build
```

**Quick troubleshooting**:
- If Vite reports unresolved imports, run `npm install` and check `node_modules` for `vue-router` / `@supabase/supabase-js`.
- If Supabase client fails at runtime, ensure `VITE_SUPABASE_*` env vars are set locally (e.g., in a `.env` file at project root).
- If pages fail to render due to import paths, search for `~` or `~/` occurrences and convert them to relative imports or add a `vite.config.js` alias mapping to `src/`.

**Pending / Next actions**:
1. (Optional) Add `vite.config.js` with `resolve.alias` mapping `~` → `/src` if you prefer keeping `~` imports.
2. Convert any remaining server endpoints to the chosen serverless signature (Vercel/Netlify/Supabase Edge Functions).
3. Run `npm run dev` locally with `VITE_SUPABASE_*` placeholders to surface any remaining runtime errors and fix iteratively.

**Notes for future AI sessions**:
- Use this file as the first context snapshot to avoid re-reading long docs.
- Check `project-docs/SETUP.md` and `project-docs/ARCHITECTURE.md` for more detailed notes.

-- End of snapshot
