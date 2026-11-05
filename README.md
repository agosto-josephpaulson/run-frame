# run-frame

Running dashboard for a Waveshare ESP32-S3-PhotoPainter (7.3" Spectra 6 e-paper).

Every hour a GitHub Action pulls activities from intervals.icu (fed by Garmin),
renders five 800x480 screens, and publishes them to GitHub Pages.
The frame (esp32-photoframe firmware, URL mode) fetches `current.jpg`, which rotates hourly.

- `fetch.py` — intervals.icu → data.json (needs secret `INTERVALS_API_KEY`)
- `render.py` — data.json → PNG/JPG screens
- `config.json` — goal, race, lifetime baseline, motivational lines

Screens: 1,000-mile goal · year calendar · latest run · race countdown · keep going.
