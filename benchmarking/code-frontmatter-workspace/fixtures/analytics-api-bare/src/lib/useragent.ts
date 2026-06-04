import type { UserAgentInfo } from "../store/store";

/**
 * Deliberately small, dependency-free user-agent parser. It is not exhaustive —
 * it covers the families that show up in real web traffic and falls back to
 * "unknown" rather than guessing. Order matters: more specific tokens are
 * checked before generic ones (e.g. Edge before Chrome, since Edge UAs also
 * contain "Chrome").
 */

interface Rule {
  name: string;
  test: RegExp;
}

const BOT_RULE = /bot|crawler|spider|crawling|slurp|bingpreview|facebookexternalhit/i;

const BROWSER_RULES: Rule[] = [
  { name: "Edge", test: /\bEdg(?:e|A|iOS)?\//i },
  { name: "Opera", test: /\bOPR\/|\bOpera\b/i },
  { name: "Samsung Internet", test: /SamsungBrowser/i },
  { name: "Chrome", test: /\bCriOS\/|\bChrome\//i },
  { name: "Firefox", test: /\bFirefox\/|\bFxiOS\//i },
  { name: "Safari", test: /\bSafari\//i },
  { name: "Internet Explorer", test: /\bMSIE\b|Trident\//i },
];

const OS_RULES: Rule[] = [
  { name: "iOS", test: /iPhone|iPad|iPod/i },
  { name: "Android", test: /Android/i },
  { name: "Windows", test: /Windows NT/i },
  { name: "macOS", test: /Mac OS X|Macintosh/i },
  { name: "ChromeOS", test: /CrOS/i },
  { name: "Linux", test: /Linux/i },
];

function classifyDevice(ua: string): UserAgentInfo["device"] {
  if (BOT_RULE.test(ua)) return "bot";
  if (/iPad|Tablet|Nexus 7|Nexus 9/i.test(ua)) return "tablet";
  if (/Android/i.test(ua) && !/Mobile/i.test(ua)) return "tablet";
  if (/Mobi|iPhone|iPod|Android.*Mobile|Windows Phone/i.test(ua)) {
    return "mobile";
  }
  if (/Windows NT|Mac OS X|CrOS|Linux/i.test(ua)) return "desktop";
  return "unknown";
}

function firstMatch(rules: Rule[], ua: string, fallback: string): string {
  for (const rule of rules) {
    if (rule.test.test(ua)) return rule.name;
  }
  return fallback;
}

/**
 * Parse a raw User-Agent header into structured fields. A missing or empty
 * header yields an "unknown" record rather than null, so downstream code never
 * has to null-check the individual fields.
 */
export function parseUserAgent(raw: string | null | undefined): UserAgentInfo {
  const ua = (raw ?? "").trim();
  if (ua === "") {
    return { browser: "unknown", os: "unknown", device: "unknown", raw: "" };
  }

  const device = classifyDevice(ua);
  // Bots frequently spoof or omit browser tokens; don't pretend to know.
  const browser =
    device === "bot" ? "bot" : firstMatch(BROWSER_RULES, ua, "unknown");
  const os = firstMatch(OS_RULES, ua, "unknown");

  return { browser, os, device, raw: ua };
}
