# scribioio.github.io

Static landing site + Apple App Site Association (AASA) host for the
[Scribio macOS app](https://github.com/johnsacco/officina).

## What lives here

| Path | Purpose |
|---|---|
| `index.html` | Public landing page (currently a placeholder). |
| `.well-known/apple-app-site-association` | The AASA file Apple fetches to verify Universal Link ownership. Required for OAuth redirects from Zoom Marketplace + future MS Graph + Webex integrations to deep-link into the Scribio app. |
| `zoom/oauth-callback.html` | Fallback page shown if a Zoom OAuth redirect ever bypasses the Universal Link interception (e.g. user clicks the auth flow on a non-macOS device). Currently displays a "returning to Scribio" message. |
| `.nojekyll` | Tells GitHub Pages to serve files verbatim (no Jekyll preprocessing — required so the `.well-known/` directory isn't filtered out). |

## OAuth redirect URL (Zoom Marketplace registration)

Use this exact URL in the Zoom Marketplace developer console:

```
https://scribioio.github.io/zoom/oauth-callback
```

## ⚠️ Apple Team ID placeholder

The AASA file currently uses the literal `TEAMID` as a placeholder.
Replace it with the actual 10-character Apple Developer Team ID
before shipping. Find your Team ID via:

```bash
# After building Scribio in Xcode:
codesign -dvv /path/to/Scribio.app 2>&1 | grep "TeamIdentifier"
# Or from your Apple Developer account: https://developer.apple.com/account
```

Then replace both occurrences in `.well-known/apple-app-site-association`.

## Deploying

GitHub Pages auto-deploys on every push to `main`. After enabling
Pages in the org settings (Settings → Pages → Source: `main` branch,
root path), the site is live at `https://scribioio.github.io/` within
a couple of minutes.

## Verifying AASA works

```bash
# Should return JSON with Content-Type: application/json
curl -I https://scribioio.github.io/.well-known/apple-app-site-association

# Apple's CDN-cached version (what iOS/macOS actually fetches):
curl -I https://app-site-association.cdn-apple.com/a/v1/scribioio.github.io
```

The CDN-cached version takes 24–48 hours to refresh after AASA changes.
