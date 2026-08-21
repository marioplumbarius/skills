# Output formats

## Supported today

### Markdown (default)

- Table of contents: a bullet list of links right under the title, one per
  `##` section, in document order — `- [Section Name](#section-name)`
  (GitHub-style anchor: lowercase, spaces to hyphens, punctuation stripped).
- Headings: `#` title, `##` sections. Don't go deeper than `###` — a blog
  post rarely needs it, and a flatter structure keeps the ToC readable.
- Inline citations: standard Markdown links, `[Label](url)`.
- Hero image: `![Alt text](path-or-url)` immediately after the ToC.
- YouTube embed: raw `<iframe>` HTML works fine inside Markdown — most
  renderers (GitHub, most blog platforms) pass it through.
- File extension: `.md`.

## Adding a new format

If the user asks for a format not listed above (HTML, plain text, a CMS's
custom syntax, etc.), don't just attempt it freehand and don't refuse it
either — offer to add it properly:

1. Tell the user this format isn't supported yet.
2. Offer to add it: a new subsection here defining how ToC, headings,
   citations, hero image, and video embed render in that format, using the
   Markdown section above as the template for what needs specifying.
3. Once they agree, write that subsection, then produce the post using it.

This keeps every format's rendering rules in one place instead of improvised
per-post, so the next post in that format is consistent with this one.
