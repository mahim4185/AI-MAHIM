# Mahim AI — Bengali-first AI Workspace

A responsive Bengali-first AI workspace prepared for the GitHub → Firebase → Render workflow. It uses plain HTML/CSS/JavaScript plus a small Python standard-library API server. The core UI needs no framework; Firebase Auth/Firestore activate only after your project, providers, rules and Render settings are configured.

**Start here:** open [`START-HERE-GITHUB-FIREBASE-RENDER-BN.md`](START-HERE-GITHUB-FIREBASE-RENDER-BN.md) for deployment steps. Optional open-source candidates (not yet integrated) are listed in [`PUBLIC-REPO-SHORTLIST-BN.md`](PUBLIC-REPO-SHORTLIST-BN.md).

## Run the preview

```bash
cd mahim-ai
python3 server.py
```

Then open `http://localhost:4173`.

Run `python3 build_preview.py` to regenerate `preview.html`, a standalone snapshot with CSS and JavaScript inlined. The app is designed to work on desktop and mobile. The live preview uses the same Python server for the static app and its API routes.

## GitHub + Render + Firebase + Publisher ads

A starter `render.yaml` is included. The intended roles are:

- **GitHub:** store the source repository and trigger deploys when code is pushed.
- **Render:** run `server.py` and serve the app/API. Connect the repository as a Render Blueprint and choose the free plan. The Render service reads its port from `PORT` and exposes `/api/health` for health checks.
- **Firebase:** the app includes Google sign-in, email/password, password reset, Firebase ID-token verification on the backend, and per-user Firestore paths for the chat list and message counter. The supplied Web App config is in `firebase-config.js`; Auth, Firestore rules and the matching Render environment value still need to be enabled in your accounts.
- **Publisher ads:** the user-supplied tags are wired in: Social Bar and Popunder are site-wide and may trigger outside the timed break; Native Banner and 300×250 load during it; Smartlink is a user-click link. Source/account approval, domain approval, consent/tracking behavior, fill and earnings have not been independently verified.

### Firebase setup

1. `firebase-config.js` now contains the Web App config provided for project `mahim-ai-99f4e`. Confirm that it belongs to your Firebase project. This is client config, not the Admin service-account JSON; restrict the key to Firebase services and use Firebase Security Rules for data protection.
2. In Firebase Authentication, enable **Google** and **Email/Password** sign-in. Add the final Render `onrender.com` hostname (and any custom domain) to **Authorized domains**.
3. Create the Firestore database, publish `firestore.rules`, and use the same Firebase Web API key as the Render environment value `FIREBASE_WEB_API_KEY`. `render.yaml` sets `REQUIRE_AUTH=true`, so the backend rejects chat/image requests without a valid Firebase sign-in token.
4. Never commit a Firebase Admin service-account private key or a provider secret API key to GitHub. The code does not need a Firebase Admin key.

The 100-message counter uses a Firestore per-user document when Firebase and Firestore are configured; without them, it falls back to a browser-local demo counter. It counts successful chat responses. The user-supplied ad tags have not been validated against an approved publisher account; confirm them in that account and test fill/consent/placement before public launch.

Render's free web services can sleep when idle and may have cold-start delays. The app loads the 40 most recently updated chats from Firestore when signed in and configured; each cloud chat stores up to 40 recent messages. Preview/guest chats stay in this browser's local storage (up to 40 chats and the latest 20 messages per chat). Users can delete one chat or clear their list from the profile.

## What works in this starter

- Responsive Mahim AI workspace shell and navigation.
- Professional profile panel with Account, Chats, and API keys tabs; the Chats tab can create, switch, and delete history, and the sidebar has the same quick chat list.
- Start a fresh chat without losing the previous one. Local preview stores chats in this browser; configured Firebase users can sync their list/messages with their own Firestore path.
- Six agent prompt presets for research, writing, coding, website design, business planning, and data help.
- BYOK chat adapters for OpenAI, Google Gemini, Anthropic, OpenRouter, Groq, and Together AI.
- API key is held only in the current browser tab's JavaScript memory. It is not written to local storage or disk. The browser sends it to `/api/chat` or `/api/image`; the server forwards it to the selected provider and does not log request bodies.
- OpenAI image-generation adapter (provider model availability, quota, and charges depend on the user's account).
- A small, local website starter builder that previews and downloads a static HTML landing page.
- Local video-file preview. The selected media file is not uploaded by this app.
- A 100-successful-chat counter with a 30-second UI lock. When Firebase and Firestore are configured, the count is per signed-in user; otherwise it is a local demo counter. The user-supplied break ad scripts are loaded in the break, while Social Bar/Popunder are site-wide; this does not guarantee an ad fill. The lock auto-unlocks at the deadline and persists through refresh.
- Optional Firebase Auth flows (Google, email/password, password reset) and backend ID-token verification, activated after `firebase-config.js` and Render settings are completed.

## Preview-only / not connected yet

This is not a production SaaS and it does not claim to be a general autonomous agent. The following require separate provider projects, credentials, and integration work:

- Firebase Web App config is now present, but Firebase Auth still requires Google/Email providers, Authorized domains, and Firestore/rules to be configured in your Firebase Console. The project has not yet been connected to your Firebase account or deployed.
- Publisher approval, verified ad-account ownership, guaranteed fill, payout setup and ad-tag behavior have not been verified. The supplied scripts are included, but test them only on your approved domain. A consent gate is not implemented; review the publisher's and applicable privacy/consent requirements before enabling live traffic.
- Video generation, live TV/channels, web search, email, external actions, hosted files, and arbitrary third-party agent repositories.
- No live Firebase project/database or public deployment is attached to this checkout. Billing, production-grade abuse prevention/rate limits, consent, and a full public SaaS operation layer still need setup.

## Provider/key notes

A provider's key works only with its provider and supported API/model. "Any API key" is not a universal standard. The starter has explicit adapters for the listed chat providers; image generation currently has an OpenAI adapter only. Video uses a separate provider-specific API and is not wired.

The server accepts a BYOK key with each request and keeps it in memory only. If this project is deployed publicly, use HTTPS, review proxy/platform logs, add authenticated sessions and account-aware rate limits, and publish a privacy policy before inviting users. Never hard-code a secret into `app.js`, `index.html`, or a public Git repository. API providers may charge for requests even if the website hosting is free.

## Production checklist

1. Verify `firebase-config.js` belongs to your Firebase project, enable Auth providers, set the matching Firebase Web API key as `FIREBASE_WEB_API_KEY` in Render, and publish `firestore.rules`.
2. Decide whether users bring their own keys or Mahim AI provides server-owned keys. For per-user keys, keep them request-scoped or use an audited encrypted storage design with a privacy policy.
3. Before public launch, add consent, abuse-report handling, a retention policy, and explicit deletion guarantees for the local/Firestore chat history already included in this starter.
4. Add provider-specific image/video/search/tool adapters. Do not advertise a feature until its API and failure handling are connected.
5. Verify every supplied ad tag in your approved publisher dashboard, test it on the authorized domain, and review consent/placement policies. A 30-second timer and ad script do not guarantee impressions or revenue.
6. Add account-level quotas, rate limits, security review, monitoring with secrets redacted, and deployment configuration before public launch.
7. Configure a hosting project and domain. This repo contains no hosting credentials and has not been deployed to a public domain.
