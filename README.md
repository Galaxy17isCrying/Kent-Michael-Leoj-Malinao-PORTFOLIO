# Kent Malinao — A Little World of Code

A playful, pixel-inspired portfolio with an image-based, pixelated game-world background, local PNG skill icons, an interactive GitHub profile card, and a Python contact API backed by MySQL.

**Live portfolio:** [https://kentmichaelleojportfolio-n3v40qfv7-asteriod-eaters.vercel.app/)

## Run locally

1. Install Python and MySQL Server.
2. From the project root, install the Python packages:

   ```sh
   python -m pip install -r requirements.txt
   ```

3. Keep your database credentials in the ignored, local `.env` file. `.env.example` documents the required variable names; never commit `.env` or paste database passwords into frontend files.
4. Create the database and contact-message table. In Command Prompt, run:

   ```bat
   mysql -u root -p < database\schema.sql
   ```

   Enter your MySQL password when prompted.
5. Start the website and API:

   ```sh
   python -m backend.app
   ```

6. Visit `http://127.0.0.1:5000`. Check `http://127.0.0.1:5000/api/health` to verify the API is running.

You can also open `index.html` directly for a visual preview; local styles and images use relative paths. The contact composer works without Flask or MySQL: it opens the visitor's email app with the message filled in. The visitor reviews and sends it from that app.

The optional `POST /api/contact` endpoint validates input, applies a five-message-per-hour per-IP limit, and stores valid messages using parameterized MySQL queries. It is not required by the portfolio's contact composer. The contact section also has a direct email link.

## APIs

- **Portfolio contact API:** Flask provides the first-party `POST /api/contact` endpoint and stores messages in MySQL.
- **GitHub REST API:** The profile card reads public repository and follower counts from GitHub's public profile endpoint. It uses no token or private credentials and has a graceful fallback when GitHub is unavailable.

To use the optional API on Vercel, configure `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_DATABASE`, `MYSQL_USER`, and `MYSQL_PASSWORD` using credentials from a reachable hosted MySQL provider. The local `.env` file is not deployed. The email-based contact composer requires no database configuration.

The contact rate limiter is process-local, intended for a single-instance portfolio. A production deployment with multiple server instances should use a shared rate-limit store and an appropriately configured reverse proxy.

Run the API tests with `python -m unittest backend.tests.test_api` from the project root.

## Portfolio content

- The education entries and skills reflect information provided by Kent. Robotics is marked proficient as requested; other skills have no inferred proficiency ratings.
- The interface uses an original, sandbox-game-inspired design with blocky ground, pixel clouds, and arcade-style buttons; it does not use Minecraft or Terraria artwork.
- The project archive links to Weather & Hazard Detection, Discord Bot, and Pokémon Pokédex. The Discord Bot card includes a keyboard-accessible slideshow of owner-supplied bot, music, and command screenshots, plus its Python, Discord, game, music, and AI-chat features.
- Contact buttons trigger a pixel minecart ride to the contact form and respect reduced-motion settings. The contact section links to Kent’s GitHub and LinkedIn profiles.
- The weather project uses Open-Meteo forecasts and a USGS earthquake feed. Some hazard-map layers contain sample data and are not official emergency alerts.
- The certificates section includes a preview and PDF for the Cisco Networking Academy IT Customer Support Basics certificate, and a viewable freeCodeCamp Python Developer Certification with an official verification link.
- The forest world background is sourced from the [Unsplash image CDN](https://images.unsplash.com/photo-1448375240586-882707db888b) and displayed with CSS pixelation, not a generated image.
- The profile portrait, school seals, certificates, and Discord bot screenshots were supplied by the portfolio owner. Project cards use a live-app capture for the weather project and a public repository preview for the Pokédex.
- Display and arcade typefaces are loaded from Google Fonts: Pixelify Sans for titles, with Nunito Sans for readable body copy and Press Start 2P for restrained game labels. System-font fallbacks are included.
- Skill logos are local PNGs under `assets/icons/`.
- Skill-icon source: [Icons8](https://icons8.com/icons). The TeamViewer badge is served from Google's favicon service.
- Edit the portfolio content in `index.html` and visual styles in `styles.css`.

## Keep credentials private

The supplied local MySQL password belongs only in `.env`, which is excluded by `.gitignore`. Do not publish `.env` or use the MySQL root account for a production deployment; create a dedicated database user with only the required permissions.
