# Markdown Parser Test Fixture

A deliberately varied Markdown document for testing common **Markdown conventions** and parser edge cases.

> **Note:** This file is a test fixture, not a specification. Expected rendering can vary by Markdown flavor (CommonMark, GFM, etc.).

## 1. Headings

# Heading level 1
## Heading level 2
### Heading level 3
#### Heading level 4
##### Heading level 5
###### Heading level 6

## 2. Paragraphs and line breaks

This is the first paragraph. It contains ordinary text, punctuation, and a URL: https://example.com.

This is a second paragraph, separated by a blank line.

This line ends with two spaces for a Markdown hard line break.  
This line should appear on the next line in renderers that support it.

This line ends with a backslash for a hard line break.\
This line should also appear on the next line.

## 3. Emphasis

- *Italic text*
- _Italic text using underscores_
- **Bold text**
- __Bold text using underscores__
- ***Bold and italic***
- ~~Strikethrough (commonly supported by GFM)~~
- `Inline code`

## 4. Lists

### Unordered list

- First item
- Second item
  - Nested item A
  - Nested item B
    - Nested item B.1
- Third item

### Ordered list

1. First step
2. Second step
   1. Nested step 2a
   2. Nested step 2b
3. Third step

### Ordered list with a non-1 start

3. Third item
4. Fourth item
5. Fifth item

### Task list (GFM)

- [x] Completed task
- [ ] Incomplete task
- [ ] Another task

## 5. Links and images

- Inline link: [Example website](https://example.com "Example title")
- Autolink: <https://example.com>
- Email link: <mailto:hello@example.com>
- Reference-style link: [OpenAI][openai]

[openai]: https://openai.com "OpenAI"

![Placeholder image alt text](https://example.com/image.png "Placeholder image title")

## 6. Blockquotes

> This is a blockquote.
>
> It has multiple paragraphs.
>
> > This is a nested blockquote.
> >
> > Nested quote continuation.

## 7. Code

Inline code can contain characters like `*`, `_`, and `#` without formatting them.

Fenced code block:

```python
def greet(name: str) -> str:
    """Return a friendly greeting."""
    return f"Hello, {name}!"

print(greet("Markdown"))
```

Fenced code block with a language label:

```json
{
  "name": "markdown-parser-fixture",
  "version": 1,
  "enabled": true,
  "tags": ["headings", "lists", "code"]
}
```

Indented code block:

    line one
    line two
        indented line three

## 8. Horizontal rules

Content above the first rule.

---

Content between rules.

***

Content below the second rule.

___

## 9. Tables (GFM)

| Feature | Syntax example | Common support |
|:--------|:--------------:|---------------:|
| Italic  | `*text*`        | Yes            |
| Bold    | `**text**`      | Yes            |
| Tables  | `\| a \| b \|`  | GFM            |
| Code    | `` `code` ``    | Yes            |

## 10. Escaping Markdown syntax

These characters are escaped so they should display literally:

- \*not italic\*
- \_not italic\_
- \# not a heading
- \[not a link\]
- 1\. Not an ordered list item
- Backslash: \\

## 11. HTML (renderer-dependent)

<div>
  <strong>Inline HTML bold text</strong>
  <p>A paragraph written in HTML.</p>
</div>

<!-- This is an HTML comment and should not normally be rendered. -->

## 12. Footnotes (extension-dependent)

Here is a sentence with a footnote reference.[^note]

[^note]: This is the footnote definition. Support depends on the parser or Markdown flavor.

## 13. Definition lists (extension-dependent)

Term One
: Definition for term one.

Term Two
: Definition for term two.
: An additional definition for term two.

## 14. Math (extension-dependent)

Inline math: $E = mc^2$

Display math:

$$
\int_0^1 x^2\,dx = \frac{1}{3}
$$

## 15. Autolinks and plain text edge cases

Bare URL: https://example.org/path?q=markdown&mode=test

Bare email: parser-test@example.org

Text with repeated spaces: alpha   beta

Unicode: café, naïve, Ελληνικά, 日本語, 🚀

Entities: &amp; &lt; &gt; &quot; &#169;

## 16. Nested mixed content

1. Main ordered item
   - Nested unordered item
   - Another nested item with **bold text** and `inline code`
     > A quote nested inside a list.
     >
     > - A list inside the quote
   - Final nested item
2. Second main item

## 17. Empty and unusual cases

### Empty section

The heading above has no content between it and this paragraph beyond the heading itself.

### Punctuation

Em dash — en dash – ellipsis … curly quotes “hello” and ‘world’.

### Literal delimiter examples

Asterisks: * ** ***  
Underscores: _ __ ___  
Backticks: ` `` ```  
Tildes: ~ ~~ ~~~

## 18. End marker

If your parser reaches this heading and the paragraph below, it has processed the whole fixture.

**End of Markdown parser test fixture.**
