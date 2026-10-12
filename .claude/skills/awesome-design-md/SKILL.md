---
name: awesome-design-md
description: Library of 84 ready-made DESIGN.md design-system analyses of real websites (Stripe, Linear, Vercel, Apple, Notion, Airbnb, Spotify, Tesla, etc.). Use when the user asks for a UI/page "that looks like <brand>", "in the style of <site>", or wants a reference design system (colors, typography, spacing, components) to build a consistent interface.
---

# Awesome DESIGN.md

Curated DESIGN.md files (Google Stitch format) from [VoltAgent/awesome-design-md](https://github.com/VoltAgent/awesome-design-md). Each one documents a site's design language: color tokens, typography scale, spacing, radii, elevation, components and usage rules.

## How to use

1. Pick the design closest to what the user asked for from the list below. If the user did not name a brand, suggest two or three that fit the brief and let them choose.
2. Read `designs/<name>/DESIGN.md` (relative to this skill's directory). The YAML front matter holds the tokens; the body explains the rules and components.
3. If the project should keep using that design language, copy the file to the project root as `DESIGN.md` so later work stays consistent.
4. Build the UI using the file's tokens (as CSS variables / Tailwind theme) and follow its component and do/don't rules. Never inline hex values that the file already names as tokens.
5. These are *inspired* analyses for visual reference: do not copy the brand's logos, trademarks or proprietary assets, and do not present the result as the real company's site.

## Available designs

`1win`, `airbnb`, `airtable`, `aljazeera`, `apple`, `binance`, `bmw`, `bmw-m`, `bugatti`, `cal`, `claude`, `clay`, `clickhouse`, `cohere`, `coinbase`, `composio`, `cursor`, `dell-1996`, `dji`, `elevenlabs`, `expo`, `ferrari`, `figma`, `framer`, `hashicorp`, `hp`, `ibm`, `intercom`, `jobright`, `kraken`, `lamborghini`, `linear.app`, `lovable`, `mastercard`, `mercury`, `meta`, `minimax`, `mintlify`, `miro`, `mistral.ai`, `mongodb`, `mydealz`, `nerdwallet`, `nike`, `nintendo-2001`, `notion`, `nvidia`, `ollama`, `opencode.ai`, `oracle`, `oura`, `pinterest`, `playstation`, `posthog`, `raycast`, `renault`, `replicate`, `resend`, `revolut`, `runwayml`, `sanity`, `sap`, `sentry`, `shopify`, `slack`, `spacex`, `spotify`, `starbucks`, `stripe`, `supabase`, `superhuman`, `tesla`, `theverge`, `together.ai`, `uber`, `vercel`, `vodafone`, `voltagent`, `warp`, `webflow`, `wired`, `wise`, `x.ai`, `zapier`
