import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

// Self-hosted Fonts
import "@fontsource-variable/bricolage-grotesque";
import "@fontsource-variable/dm-sans";
import "@fontsource/ibm-plex-mono/400.css";
import "@fontsource/ibm-plex-mono/500.css";

// Design System Styles
import "./styles/tokens.css";
import "./styles/base.css";
import "./styles/motion.css";

import App from "./App.jsx";

createRoot(document.getElementById("root")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
