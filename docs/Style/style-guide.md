# jameskilby.co.uk — Blog Style Guide

> Version 1.0 · Last updated: June 2026  
> Covers: Voice & tone · Formatting & structure · Code conventions · Visual design

---

## Voice & tone

Your blog is authoritative but approachable — a practitioner talking to peers, not a textbook or a sales deck.

### Write in first person, plainly

Use "I", "my lab", "I found". You're sharing your own real experience. Avoid corporate passives like "it was observed that".

**Do:** "I ran into this issue when expanding my TrueNAS pool and it took longer than expected."  
**Don't:** "Users may encounter this issue when expanding storage pools in TrueNAS environments."

### State the problem before the solution

Open every post by explaining what you were trying to do and what went wrong. Readers need context to know if a post is relevant to them.

### Avoid filler openers

Don't open with "In this post, we'll explore…" or "VMware is a powerful platform." Get to the problem in sentence one or two.

**Do:** "My VCSA had expired SSL certs and I couldn't log in. Here's how I recovered it without reinstalling."  
**Don't:** "SSL certificates are an important part of keeping your vSphere environment secure. In this post we'll look at how to renew them."

### Light British English — but accessible globally

Spell "colour", "centre", "authorise" — but avoid idioms that won't travel. Your audience is UK/US split.

### No overselling or hype

Don't call things "game-changing", "revolutionary", or "incredibly powerful". If something is good, show it — don't tell it.

### It's OK to admit difficulty

Phrases like "this took me longer than I'd like to admit" are part of your voice. Real experience beats polished tutorials.

---

## Formatting & structure

### Post structure

Every technical post should follow this arc:

1. **Problem** — what you were trying to do and what broke
2. **Context** — your environment, versions, why it matters
3. **Steps** — numbered, actionable, one action per step
4. **Result** — what the outcome was; optionally, what you'd do differently

### Headings

- H1 is the post title only — never use it inside a post body
- H2 for major sections, H3 for sub-steps
- Never skip heading levels
- Keep headings descriptive, not clever — "Install the agent" not "Getting things moving"
- Don't use H2/H3 for single-sentence sections; fold into the previous section or drop the heading

### Callout blocks

Use border-left accent callout blocks for:

| Type | When to use |
|---|---|
| ⚠ Warning | Risk of data loss or irreversible action |
| ℹ Note | Version-specific or environment-specific caveat |
| 💡 Tip | Optional shortcut or efficiency improvement |

Don't use callouts for general information — they lose their signal value if overused.

### Publish timing

Publish Tuesday–Thursday, 9–10 AM GMT. Your UK/US audience peaks mid-week, mid-morning UK time. Schedule drafts rather than publishing at odd hours.

### Meta description

- 140–155 characters
- Written as an answer, not a topic description
- Target keyword in the first 60 characters
- Present tense

**Example:** "How to recover a VCSA when SSL certificates have expired — step-by-step using the Broadcom vCert tool."

### Alt text

Describe what the image shows, not what it is generically.

**Do:** "vCenter hardware status panel showing NIC POST error 928 in slot 5"  
**Don't:** "screenshot of VMware vCenter"

Filename convention: `vcenter-error-928-nic-slot5.webp` — kebab-case, descriptive, no spaces.

---

## Code conventions

### Always specify language on fenced code blocks

Use ` ```bash `, ` ```yaml `, ` ```powershell `, ` ```python ` — never a bare ` ``` `.

### Add a comment header to every snippet

One-line comment at the top: what the file is and what it does. Readers often arrive mid-post from search.

```bash
# deploy-portainer-agent.yml — Ansible task to deploy Portainer Agent 2.40.0
```

### Don't expose real credentials or hostnames

Replace real values with clearly-marked placeholders:

- `YOUR_API_KEY`
- `vcenter.yourdomain.com`
- `<YOUR_PASSWORD>`

Never use real internal IPs or hostnames, even in examples.

### Inline code for all commands, paths, and config keys

When mentioning a command, flag, path, or config key inside a sentence, always wrap it in backticks.

**Do:** "Run `growpart`, then edit `/etc/fstab` and set `svga.present = "FALSE"`."  
**Don't:** Leaving commands as plain text in a sentence.

### State versions explicitly

Note the version you're working with near the top of every post — e.g. vSphere 8.0 U3, Ubuntu 24.04, Portainer Agent 2.40.0. Technical posts go stale fast; a version stamp tells readers when to trust advice.

### Show expected output

Where possible, show the expected terminal output or UI state after a step in a separate block:

```bash
# expected output
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda3       200G   18G  172G  10% /
```

### Don't mix commands and output in the same block

Readers copy code blocks whole. If output is in the same block as the command, they'll paste the output too.

---

## Visual design

### Images: always WebP, max 1200px wide

Convert PNGs and JPEGs to WebP before publishing. Target under 200 KB for screenshots. Use lossless WebP for diagrams with text, lossy for photos.

### Crop screenshots tightly

Crop to the UI element or terminal output in question — don't paste a full 4K screenshot when the relevant area is 20% of it. Add a red rectangle or arrow annotation if something needs highlighting.

### Open Graph image

- Size: 1200×630px
- Use a consistent branded template: dark background, title text, watermark/logo
- Always use absolute URLs in OG tags: `https://jameskilby.co.uk/images/...`
- Never use relative paths — they break link previews on LinkedIn, Slack, and Twitter/X

### No stock photos for technical posts

Real screenshots from your actual lab carry more credibility than generic server rack photos.

### Architecture diagrams: pick one tool and stick with it

Use draw.io, Excalidraw, or Mermaid in markdown — but be consistent across posts. A unified visual style makes the blog feel cohesive.

### Typography

- Body text: ≥ 16px, line-height 1.6–1.7
- Code blocks: monospace, minimum 14px, distinct background colour to visually separate from prose
- Two font weights maximum: regular and medium/semi-bold

---

## Quick reference card

| Rule | Standard |
|---|---|
| Voice | First person, plain English |
| Opener | Problem statement, no filler |
| Spelling | British English |
| Post structure | Problem → Context → Steps → Result |
| Publish window | Tue–Thu, 9–10 AM GMT |
| Meta description | 140–155 chars, keyword in first 60 |
| Code blocks | Always specify language |
| Version stamping | Required — near top of every post |
| Image format | WebP, max 1200px, under 200 KB |
| OG image | 1200×630px, absolute URL |
| OG URL | Always absolute (`https://jameskilby.co.uk/...`) |
| Credentials | Placeholders only — never real values |
