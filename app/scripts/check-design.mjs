#!/usr/bin/env node
/**
 * check-design.mjs: Design system compliance linter for SpeechCoach.
 * Enforces visual constraints: no forbidden hues (190-320°), no gradients,
 * no border-radius < 8px, no raw hex outside tokens.css, no emoji in JSX,
 * no glassmorphism / backdrop-filter, no transition: all.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const srcDir = path.resolve(__dirname, "../src");
const tokensPath = path.resolve(srcDir, "styles/tokens.css");

let errors = [];

function hexToHsl(hex) {
  let c = hex.replace("#", "");
  if (c.length === 3) {
    c = c.split("").map((x) => x + x).join("");
  }
  if (c.length !== 6) return null;
  const num = parseInt(c, 16);
  const r = (num >> 16) & 255;
  const g = (num >> 8) & 255;
  const b = num & 255;

  const rNorm = r / 255;
  const gNorm = g / 255;
  const bNorm = b / 255;

  const max = Math.max(rNorm, gNorm, bNorm);
  const min = Math.min(rNorm, gNorm, bNorm);
  const delta = max - min;

  let h = 0;
  let s = 0;
  const l = (max + min) / 2;

  if (delta !== 0) {
    s = l > 0.5 ? delta / (2 - max - min) : delta / (max + min);
    switch (max) {
      case rNorm:
        h = (gNorm - bNorm) / delta + (gNorm < bNorm ? 6 : 0);
        break;
      case gNorm:
        h = (bNorm - rNorm) / delta + 2;
        break;
      case bNorm:
        h = (rNorm - gNorm) / delta + 4;
        break;
    }
    h *= 60;
  }
  return { h, s: s * 100, l: l * 100 };
}

// 1. Check tokens.css for prohibited hues (190° to 320° with saturation > 10%)
if (fs.existsSync(tokensPath)) {
  const content = fs.readFileSync(tokensPath, "utf-8");
  const lines = content.split("\n");
  lines.forEach((line, idx) => {
    const hexMatches = line.match(/#[0-9a-fA-F]{3,8}\b/g);
    if (hexMatches) {
      hexMatches.forEach((hex) => {
        const hsl = hexToHsl(hex);
        if (hsl) {
          if (hsl.h >= 190 && hsl.h <= 320 && hsl.s > 10) {
            errors.push(
              `${path.relative(srcDir, tokensPath)}:${idx + 1} - Prohibited hue ${Math.round(hsl.h)}° with saturation ${Math.round(hsl.s)}% in hex "${hex}" (Rule: no hue between 190° and 320°)`
            );
          }
        }
      });
    }
  });
}

// 2. Walk src/ and scan all files
function walk(dir) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      walk(fullPath);
    } else if (/\.(css|jsx|js)$/.test(entry.name)) {
      lintFile(fullPath);
    }
  }
}

const emojiRegex = /[\u{1F300}-\u{1F64F}\u{1F680}-\u{1F6FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}\u{1F900}-\u{1F9FF}\u{1F1E0}-\u{1F1FF}]/u;

function lintFile(filePath) {
  const isTokensFile = path.resolve(filePath) === tokensPath;
  const content = fs.readFileSync(filePath, "utf-8");
  const lines = content.split("\n");
  const relPath = path.relative(srcDir, filePath);

  lines.forEach((line, idx) => {
    const lineNum = idx + 1;
    const trimmed = line.trim();

    // Ignore single line comments
    if (trimmed.startsWith("//") || trimmed.startsWith("/*")) return;

    // Check for gradients
    if (/gradient\s*\(/i.test(line)) {
      errors.push(`${relPath}:${lineNum} - Forbidden gradient found: "${trimmed}"`);
    }

    // Check for backdrop-filter
    if (/backdrop-filter/i.test(line)) {
      errors.push(`${relPath}:${lineNum} - Forbidden backdrop-filter found: "${trimmed}"`);
    }

    // Check for transition: all
    if (/transition\s*:\s*all\b/i.test(line)) {
      errors.push(`${relPath}:${lineNum} - Forbidden transition: all found: "${trimmed}"`);
    }

    // Check for raw hex colors outside tokens.css
    if (!isTokensFile) {
      // Allow hex inside url(...) or SVG path definitions if any, but flag CSS/JSX color assignments
      const hexMatches = line.match(/#[0-9a-fA-F]{3,8}\b/g);
      if (hexMatches) {
        // Exception: allow true black/white rgba or comments if necessary, but flag all hardcoded color hexes
        hexMatches.forEach((hex) => {
          errors.push(
            `${relPath}:${lineNum} - Hardcoded hex code "${hex}" outside tokens.css. Use design tokens (var(--...)).`
          );
        });
      }
    }

    // Check for border-radius under 8px
    if (/border-radius\s*:/i.test(line)) {
      const radiusMatch = line.match(/border-radius\s*:\s*([^;]+);/i);
      if (radiusMatch) {
        const valStr = radiusMatch[1].trim();
        // Check for literal px values
        const pxMatches = valStr.match(/\b(\d+)\s*px\b/g);
        if (pxMatches) {
          pxMatches.forEach((pxVal) => {
            const num = parseInt(pxVal, 10);
            if (num > 0 && num < 8) {
              errors.push(
                `${relPath}:${lineNum} - Forbidden border-radius "${pxVal}" under 8px (Minimum radius is 8px or var(--r-*))`
              );
            }
          });
        }
      }
    }

    // Check for emojis in JSX / JS files
    if (/\.(jsx|js)$/.test(filePath) && emojiRegex.test(line)) {
      errors.push(
        `${relPath}:${lineNum} - Forbidden emoji character found in JSX/JS. Use lucide-react icons.`
      );
    }
  });
}

walk(srcDir);

if (errors.length > 0) {
  console.error(`\n❌ Design Linter Failed with ${errors.length} violation(s):\n`);
  errors.forEach((err) => console.error(`  • ${err}`));
  console.error("");
  process.exit(1);
} else {
  console.log(`\n✅ Design Linter: All design system checks passed!\n`);
  process.exit(0);
}
