---
order: 90
icon: beaker
tags: [docs, documentation, retype, layout]
---
# Documentation Layout
## Introduction

Retype uses the directory structure as a base for the sidebar and site layout. If you need to add a new page, just create a new markdown page inside the appropriate subfolder. For example, to create a file called `test.md` under the heading of Contributing, create the file at the following path: `docs/contributing/test.md`. It will automatically get picked up and displayed under the Contributing header!

### Header Block

Every page needs to start with a brief block so Retype knows how to display it.

```markdown
---
order: 50
icon: book
tags: [dev, development, docs]
---
```

That's the header block from this very page! Here's what those keys do:

* `order`: The order of the pages in the sidebar. Higher numbers are displayed higher in the list and are compared against the `order` keys in the other pages.
* `icon`: Pick any icon from [GitHub's icon list](https://primer.github.io/octicons/) to use it as the icon on the sidebar. Click on the icon you like to get its name.
* `tags`: Any searchable tags you want to apply to this page -- tags are searchable on the site, so use as many tags as you feel are necessary!

After that, there should be a few specific sections so that everyone understands what the page is for and what information we are trying to share.

### Introduction

The introduction serves a very important purpose -- it tells the reader why they should read it! The introduction has a very specific layout:

* one or two sentences that explain what the page is for
* "In this page, ..." Explain exactly what the reader will do or what they will learn by reading this

For example:

> "In this page, you will install and configure `pyenv`, Python, and Poetry, the three tools you need to work on Alexandria on your computer."

In one sentence, we establish what we will learn on the page ("`pyenv`, Python, and Poetry"), what we are going to do with them ("install and configure"), and why we need to know this information ("the three tools you need to work on Alexandria on your computer.") By the end of the page, we have installed and configured the three programs.

### Prerequisites

The Prerequisites section should list every single _external_ thing that a reader needs before following the page of documentation.

!!!
If we have to send the reader away from the docs to do something, we should only do it at the very beginning.

Everything else should be accomplished inside the docs.
!!!

In the Prerequisites, use bullet points (`*` or `-` -- see the [markdown spec for lists](https://www.markdownguide.org/basic-syntax/#unordered-lists) for more information) to list out every piece of technology or process that the reader needs to do, with exact links to documentation that explain how to achieve what should happen. For example:

* Install X as described by [steps one and two of this documentation]()
* This [third party software]()
* A laptop computer with a fingerprint reader

Any prerequisites should be extremely clear and if it contains a link, make the link part of the actual requirement so that it's clear what the reader is clicking on. It's better to have the link span multiple words as shown above than to have something like:

* This third party software ([click here]())

If another page hosted here in the documentation is required as a prerequisite, link directly to that page using the `!ref` syntax:

```markdown
[!ref](doc_layout.md)
```

It will render out to this:

[!ref](doc_layout.md)

### Rest of the Docs

The rest of the document should be separated out into logical sections using the double `##` to act as a "level two" header. There should only be one "level one" header -- the `#` -- and it should be at the very top of the page.

You can see a complete template, ready for copying and pasting, at the Example Page.

[!ref](example_page.md)
