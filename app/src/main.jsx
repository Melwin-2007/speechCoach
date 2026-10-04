import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

// Self-hosted Fonts
import "@fontsource/geist-sans/400.css";
import "@fontsource/geist-sans/500.css";
import "@fontsource/geist-sans/600.css";
import "@fontsource/geist-sans/700.css";
import "@fontsource/geist-mono/400.css";
import "@fontsource/geist-mono/500.css";

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
