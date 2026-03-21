# Skill Journey AI Frontend

This is a React + Vite + TypeScript frontend for Skill Journey AI.

## Auth behavior

- Login stores a demo `user` object in `localStorage`.
- Protected routes (`/upload`, `/quiz`, `/dashboard`) require a logged-in user.
- Root `/` redirects to `/login` if not logged in, otherwise to `/upload`.

## API architecture

- Components call functions from `src/lib/api.ts` (public frontend interface).
- `api.ts` delegates all network calls to `src/lib/middlewareApi.ts`.
- The middleware layer talks to your backend middleware service, which holds
	all external API keys and calls any third-party providers.

This keeps secrets on the server and ensures the frontend never calls external
APIs directly.

### Configuration

- `VITE_API_BASE_URL` (optional): base URL for the middleware service.
	- Defaults to `/middleware` for same-origin setups.
	- Example: `VITE_API_BASE_URL="https://your-backend.example.com/middleware"`.

All middleware endpoints are `POST` with JSON bodies:

- `/analyze-profile`
- `/generate-test`
- `/evaluate-test`
- `/compute-path`
- `/chat`
