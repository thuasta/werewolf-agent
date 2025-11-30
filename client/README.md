# Client

The visualization part of the project. Main features should include:

- Spectators watching a running game.
- Replay a game.
- Allowing human player participating a game.

<!-- TODO: finish -->

---

- UI is functional and was validated locally with `npm run dev`.
- A local mock game engine (`src/services/mockGameEngine.ts`) simulates `game_state` streaming and handles human actions for demo purposes.

Notes about the mock engine
- `src/services/mockGameEngine.ts` is a front-end mock used for local demos. It exposes:
  - `subscribeToGame(callback)` — subscribe to game state updates
  - `startGameLoop()` — start the demo loop
  - `resetGame()` — reset state
  - `sendHumanAction(decision)` — log/handle human actions
- To integrate with a real backend, replace or adapt this module to use WebSockets / SSE or HTTP POSTs according to back-end protocol.
