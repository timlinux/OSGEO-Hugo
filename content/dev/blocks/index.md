---
type: "page"
title: "Block & Shortcode Gallery"
subtitle: "Every content block this site provides, with the syntax to use it"
description: "Live demos of all Hugo shortcodes available in this project, each followed by the exact markup that produced it."
draft: false
heroSize: "is-small"
HasBanner: true
---

<!-- GENERATED FILE - DO NOT EDIT BY HAND.
     Regenerate with: osgeo blocks
     Source of truth: data/shortcodes.json -->

This gallery is generated from `data/shortcodes.json` — the same
registry that powers the Neovim `:InsertBlock` picker. Each entry shows
the rendered block followed by the exact markup that produced it.

## Layout blocks

### `block-grid`

Renders a colored section with inner markdown split by ---- into up to three columns/blocks, with optional subtitle, background image, and bottom bar.

Parameters: `backgroundColor` — Bulma background color name (default dark) · `backgroundImage` — Site-relative image path used as the block background · `classes` — Extra CSS classes on the content div · `isSection` — Wrap the content in a padded section element (default true) · `sectionClasses` — Extra CSS classes on the section element · `showBottomBar` — Add a bottom-bar class to the content (default false) · `subtitle` — Small bold kicker text above the first column · `subtitleColor` — Bulma color name for the kicker text (default complementary7) · `textColor` — Bulma text color name (default white)

{{< block-grid subtitle="WHY OSGEO" backgroundColor="dark" textColor="white" >}}
## Open Software
Free geospatial tools for everyone.
----
## Open Community
A welcoming global network of contributors.
{{< /block-grid >}}

```text
{{</* block-grid subtitle="WHY OSGEO" backgroundColor="dark" textColor="white" */>}}
## Open Software
Free geospatial tools for everyone.
----
## Open Community
A welcoming global network of contributors.
{{</* /block-grid */>}}
```

---

### `box-start`

Opens a Bulma box container with optional corner ribbon and background image; close with box-end, which appends a footer bar unless disabled.

Parameters: `backgroundImage` — Site-relative image path used as the box background · `class` — Custom classes for the box (prefixed with 'content'); overrides the default container styling · `classes` — Alternative spelling of class, used when class is not given · `no-footer` — On box-end: any non-empty value suppresses the footer bar · `ribbon` — Optional ribbon label text shown at the box corner · `ribbon-class` — Bulma classes for the ribbon (default is-info is-small)

{{< box-start ribbon="New" ribbon-class="is-info is-small" >}}
This is **boxed content** with a ribbon.
{{< box-end >}}

```text
{{</* box-start ribbon="New" ribbon-class="is-info is-small" */>}}
This is **boxed content** with a ribbon.
{{</* box-end */>}}
```

---

### `column-start`

Opens a flex Bulma column inside a columns container; close with column-end.

Parameters: `animate` — true to add scroll animation classes (default false) · `class` — Extra CSS classes for the column

{{< columns-start >}}
{{< column-start class="is-6" >}}
Left column content.
{{< column-end >}}
{{< column-start class="is-6" >}}
Right column content.
{{< column-end >}}
{{< columns-end >}}

```text
{{</* columns-start */>}}
{{</* column-start class="is-6" */>}}
Left column content.
{{</* column-end */>}}
{{</* column-start class="is-6" */>}}
Right column content.
{{</* column-end */>}}
{{</* columns-end */>}}
```

---

### `columns-start`

Opens a centered multiline Bulma columns container; close with columns-end.

Parameters: `id` — Optional HTML id for the container

{{< columns-start id="feature-columns" >}}
{{< column-start >}}
First column.
{{< column-end >}}
{{< column-start >}}
Second column.
{{< column-end >}}
{{< columns-end >}}

```text
{{</* columns-start id="feature-columns" */>}}
{{</* column-start */>}}
First column.
{{</* column-end */>}}
{{</* column-start */>}}
Second column.
{{</* column-end */>}}
{{</* columns-end */>}}
```

---

### `content`

Renders inner markdown inside a full-width Bulma column with content typography.

Parameters: `classes` — Extra CSS classes for the column

{{< content classes="has-text-centered" >}}
Some **markdown** content rendered in a full-width column.
{{< /content >}}

```text
{{</* content classes="has-text-centered" */>}}
Some **markdown** content rendered in a full-width column.
{{</* /content */>}}
```

---

### `content-panel-grid-start`

Opens a responsive grid container for content panels with a configurable column count; close with content-panel-grid-end.

Parameters: `columns` — Number of grid columns via the --grid-columns CSS variable (default 3)

{{< content-panel-grid-start columns="2" >}}
{{< content-panel-start title="Panel One" >}}
First panel content.
{{< content-panel-end >}}
{{< content-panel-start title="Panel Two" >}}
Second panel content.
{{< content-panel-end >}}
{{< content-panel-grid-end >}}

```text
{{</* content-panel-grid-start columns="2" */>}}
{{</* content-panel-start title="Panel One" */>}}
First panel content.
{{</* content-panel-end */>}}
{{</* content-panel-start title="Panel Two" */>}}
Second panel content.
{{</* content-panel-end */>}}
{{</* content-panel-grid-end */>}}
```

---

### `content-panel-start`

Opens a styled content panel with optional icon, title, subtitle, and variant styling; close with content-panel-end, which can add a footer button.

Parameters: `button-class` — On content-panel-end: footer button class (default is-osgeo-primary) · `button-link` — On content-panel-end: footer button URL · `button-text` — On content-panel-end: footer button label · `icon` — Optional Font Awesome icon class shown in the header · `id` — Optional HTML id for the panel · `subtitle` — Optional subtitle under the title · `title` — Panel title shown in the header · `variant` — Space-separated style variants: featured, teal, cyan, amber, dark, compact

{{< content-panel-start title="Get Involved" subtitle="Everyone is welcome" icon="fa-solid fa-star" variant="featured" >}}
Join a working group, contribute code, or help with **documentation**.

- Attend a local chapter meeting
- Sponsor a project
{{< content-panel-end button-text="Learn More" button-link="/community/" >}}

```text
{{</* content-panel-start title="Get Involved" subtitle="Everyone is welcome" icon="fa-solid fa-star" variant="featured" */>}}
Join a working group, contribute code, or help with **documentation**.

- Attend a local chapter meeting
- Sponsor a project
{{</* content-panel-end button-text="Learn More" button-link="/community/" */>}}
```

---

### `content-start`

Opens a content section with an Edit-on-GitHub button and optional page sidebar layout; close with content-end.

Parameters: `animate` — true to add scroll animation classes (default false) · `classes` — CSS classes for the inner container (default content) · `header` — Read from params but not used in the output · `sidebar` — Read from params but the sidebar is driven by the page's sidebar front-matter param instead

{{< content-start classes="content" >}}
## About this page
Regular **markdown** content goes here.
{{< content-end >}}

```text
{{</* content-start classes="content" */>}}
## About this page
Regular **markdown** content goes here.
{{</* content-end */>}}
```

---

### `platform-content-start`

Opens a hidden tabpanel div tied to a platform key (shown by platform-detection JS); close with platform-content-end.

Parameters: `platform` — Platform key stored in the data-platform attribute (e.g. windows, macos, linux)

_This block depends on site data or external services and is not demoed inline._

```text
{{</* platform-content-start platform="windows" */>}}
Windows-specific download instructions.
{{</* platform-content-end */>}}
```

---

### `rich-box`

Renders a rich container div with optional icon and inner content as markdown or raw HTML.

Parameters: `icon` — Optional Font Awesome icon class shown at the top · `id` — Optional HTML id for the container · `layoutClass` — Layout/width CSS class added to the rich container · `mode` — html to render inner content raw; otherwise inner content is markdownified

{{< rich-box layoutClass="third" icon="fas fa-globe" >}}
Some **markdown** content in a rich box.
{{< /rich-box >}}

```text
{{</* rich-box layoutClass="third" icon="fas fa-globe" */>}}
Some **markdown** content in a rich box.
{{</* /rich-box */>}}
```

---

### `rich-box-start`

Opens a rich container div with optional icon, for wrapping other shortcodes; close with rich-box-end.

Parameters: `icon` — Optional Font Awesome icon class shown at the top · `id` — Optional HTML id for the container · `layoutClass` — Layout/width CSS class added to the rich container

{{< rich-box-start layoutClass="third" icon="fas fa-map" >}}
Content inside the rich box.
{{< rich-box-end >}}

```text
{{</* rich-box-start layoutClass="third" icon="fas fa-map" */>}}
Content inside the rich box.
{{</* rich-box-end */>}}
```

---

### `rich-content`

Renders inner markdown inside a themed cont div used within rich boxes.

Parameters: `themeClass` — Theme CSS class added to the cont div

{{< rich-content themeClass="is-light" >}}
Some **markdown** content.
{{< /rich-content >}}

```text
{{</* rich-content themeClass="is-light" */>}}
Some **markdown** content.
{{</* /rich-content */>}}
```

---

### `rich-content-start`

Opens a themed cont div for wrapping other shortcodes inside rich boxes; close with rich-content-end.

Parameters: `themeClass` — Theme CSS class added to the cont div

{{< rich-content-start themeClass="is-light" >}}
Wrapped content here.
{{< rich-content-end >}}

```text
{{</* rich-content-start themeClass="is-light" */>}}
Wrapped content here.
{{</* rich-content-end */>}}
```

---

### `rich-right`

Renders inner content unchanged inside a rich-right aligned div.

{{< rich-right >}}
<span>Right-aligned content</span>
{{< /rich-right >}}

```text
{{</* rich-right */>}}
<span>Right-aligned content</span>
{{</* /rich-right */>}}
```

---

### `rich-right-start`

Opens a rich-right aligned div for wrapping other shortcodes; close with rich-right-end.

{{< rich-right-start >}}
Right-side content here.
{{< rich-right-end >}}

```text
{{</* rich-right-start */>}}
Right-side content here.
{{</* rich-right-end */>}}
```

---

### `tab-content-start`

Opens a tab content panel div identified by content-tab-N, toggled by the tabs shortcode; close with tab-content-end.

Parameters: `class` — Optional CSS class for the panel div · `tab` — Tab number matching a tab defined in the tabs shortcode (builds id content-tab-N)

{{< tabs tab1="Overview" tab2="Details" >}}
{{< tab-content-start tab="1" >}}
Overview content.
{{< tab-content-end >}}
{{< tab-content-start tab="2" >}}
Detail content.
{{< tab-content-end >}}

```text
{{</* tabs tab1="Overview" tab2="Details" */>}}
{{</* tab-content-start tab="1" */>}}
Overview content.
{{</* tab-content-end */>}}
{{</* tab-content-start tab="2" */>}}
Detail content.
{{</* tab-content-end */>}}
```

---

## Content blocks

### `block`

Renders a Bulma notification banner section with title/subtitle, optional side image block, optional link ribbon, and a collapsible read-more area fed by inner markdown.

Parameters: `animate` — true to add scroll animation classes (default false) · `class` — Bulma color/modifier class for the block (default is-primary) · `image` — Page-bundle image resource name used as the side/cover block background (matched via .Page.Resources.GetMatch) · `link` — Optional URL for the link ribbon (local path or http/mailto) · `link-text` — Text for the link ribbon · `sub-block-side` — Placement of the title sub-block: left, right, cover, bottom, or none (default none) · `subtitle` — Banner subtitle text shown in the central block · `subtitle-size` — Bulma subtitle size class (default is-4) · `title` — Banner title text (shown uppercase in side block, or centered when sub-block-side=cover) · `title-size` — Bulma title size class (default is-2)

{{< block title="Our Mission" subtitle="Empowering everyone with open source geospatial software" class="is-primary" sub-block-side="left" >}}
OSGeo is a **not-for-profit organization** fostering global adoption of open geospatial technology.
{{< /block >}}

```text
{{</* block title="Our Mission" subtitle="Empowering everyone with open source geospatial software" class="is-primary" sub-block-side="left" */>}}
OSGeo is a **not-for-profit organization** fostering global adoption of open geospatial technology.
{{</* /block */>}}
```

---

### `block-section`

Full-width fluid variant of the block banner: notification section with title/subtitle, optional side or cover image, optional background image, link ribbon, and collapsible inner markdown.

Parameters: `animate` — true to add scroll animation classes (default false) · `backgroundImage` — Site-relative image path used as the whole-block background · `class` — Bulma color/modifier class for the block (default is-primary) · `image` — Page-bundle image resource name for the side/cover block background · `link` — Optional URL for the link ribbon · `link-text` — Text for the link ribbon · `sub-block-side` — Placement of the title sub-block: left, right, cover, bottom, or none (default none) · `subtitle` — Banner subtitle text shown in the central block · `subtitle-size` — Bulma subtitle size class (default is-5) · `title` — Banner title text · `title-size` — Bulma title size class (default is-2)

{{< block-section title="Get Involved" subtitle="Join a global community of geospatial developers" class="is-primary" sub-block-side="left" backgroundImage="/img/osgeo/osgeo-logo.png" >}}
Everyone is welcome to **contribute** to OSGeo projects.
{{< /block-section >}}

```text
{{</* block-section title="Get Involved" subtitle="Join a global community of geospatial developers" class="is-primary" sub-block-side="left" backgroundImage="/img/osgeo/osgeo-logo.png" */>}}
Everyone is welcome to **contribute** to OSGeo projects.
{{</* /block-section */>}}
```

---

### `button`

Renders a single Bulma button link with optional Font Awesome icon.

Parameters: `class` — Bulma color class (default is-primary) · `fullwidth` — true to make the button full width (default false) · `icon` — Optional Font Awesome icon class · `link` — Target URL (passed through absURL) · `text` — Button label text

{{< button text="Download OSGeoLive" link="/download/" class="is-primary" icon="fas fa-download" >}}

```text
{{</* button text="Download OSGeoLive" link="/download/" class="is-primary" icon="fas fa-download" */>}}
```

---

### `button-bar`

Renders a centered row of one or two large buttons; supports named button1/button2 params or legacy positional icon:text:link arguments.

Parameters: `0` — Legacy fallback: positional args in the form icon-class:label:link (used only when no named button params are given) · `animate` — true to add scroll animation classes (default false) · `button1-class` — Bulma class of the first button (default is-osgeo-primary) · `button1-link` — URL of the first button (default #) · `button1-text` — Label of the first button · `button2-class` — Bulma class of the second button (default is-osgeo-secondary) · `button2-link` — URL of the second button (default #) · `button2-text` — Label of the second button

{{< button-bar button1-text="Join OSGeo" button1-link="/community/" button2-text="Donate" button2-link="/donate/" >}}

```text
{{</* button-bar button1-text="Join OSGeo" button1-link="/community/" button2-text="Donate" button2-link="/donate/" */>}}
```

---

### `csv-table`

Renders a roadmap-style HTML table from a CSV site resource (file param) or from inner CSV content, with :rm-xxx: cell class markers.

Parameters: `file` — Path to a CSV file in site assets (resources.Get); when omitted, the inner content is unmarshalled instead

{{< csv-table >}}
Milestone,Date,Status
Feature freeze,2026-03-01,:rm-done:Complete
Release,2026-06-01,Planned
{{< /csv-table >}}

```text
{{</* csv-table */>}}
Milestone,Date,Status
Feature freeze,2026-03-01,:rm-done:Complete
Release,2026-06-01,Planned
{{</* /csv-table */>}}
```

---

### `cta-box`

Renders a call-to-action section with a title, optional subtitle, and up to two large white buttons.

Parameters: `button1-link` — URL of the first button (default #) · `button1-text` — Label of the first button · `button2-link` — URL of the second button (default #) · `button2-text` — Label of the second (outlined) button · `subtitle` — Optional CTA subtitle paragraph · `title` — CTA heading (default Join Us)

{{< cta-box title="Ready to map the world?" subtitle="Join thousands of contributors building open geospatial software." button1-text="Get Started" button1-link="/community/" button2-text="Donate" button2-link="/donate/" >}}

```text
{{</* cta-box title="Ready to map the world?" subtitle="Join thousands of contributors building open geospatial software." button1-text="Get Started" button1-link="/community/" button2-text="Donate" button2-link="/donate/" */>}}
```

---

### `feature`

Renders a decorated feature row with a heading, lead text, large image, and three captioned text columns beneath.

Parameters: `col-text-1` — Text of the first sub-column · `col-text-2` — Text of the second sub-column · `col-text-3` — Text of the third sub-column · `col-title-1` — Title of the first sub-column · `col-title-2` — Title of the second sub-column · `col-title-3` — Title of the third sub-column · `img` — Image path (passed through absURL) · `order` — Decoration variant number used in left-deco-N and deco-block-N CSS classes · `text` — Lead paragraph text · `title` — Feature heading

{{< feature order="1" title="Open Standards" text="OSGeo projects implement open standards for interoperability." img="/img/osgeo/osgeo-logo.png" col-title-1="Interoperable" col-text-1="Works with OGC standards." col-title-2="Free" col-text-2="No licence fees, ever." col-title-3="Community" col-text-3="Built by volunteers worldwide." >}}

```text
{{</* feature order="1" title="Open Standards" text="OSGeo projects implement open standards for interoperability." img="/img/osgeo/osgeo-logo.png" col-title-1="Interoperable" col-text-1="Works with OGC standards." col-title-2="Free" col-text-2="No licence fees, ever." col-title-3="Community" col-text-3="Built by volunteers worldwide." */>}}
```

---

### `hero-banner`

Renders a large hero section with a positional title and inner content as subtitle, followed by a box showing the latest news page title.

Parameters: `0` — Hero title text (positional)

{{< hero-banner "Welcome to OSGeo" >}}
The Open Source Geospatial Foundation
{{< /hero-banner >}}

```text
{{</* hero-banner "Welcome to OSGeo" */>}}
The Open Source Geospatial Foundation
{{</* /hero-banner */>}}
```

---

### `image`

Renders a single full-width image inside a section/tile container.

Parameters: `animate` — true (default) to add scroll animation classes · `image` — Image URL or path to display

{{< image image="/img/osgeo/osgeo-logo.png" >}}

```text
{{</* image image="/img/osgeo/osgeo-logo.png" */>}}
```

---

### `image-bar`

Renders a horizontal bar of small rounded images with centered captions, one per positional caption:image-url argument.

Parameters: `0` — Positional args, each in the form caption:image-url (repeat for more tiles) · `animate` — true to add scroll animation classes (cannot be combined with positional args)

{{< image-bar "Community:/img/osgeo/osgeo-logo.png" "Projects:/img/osgeo/osgeo-logo.png" >}}

```text
{{</* image-bar "Community:/img/osgeo/osgeo-logo.png" "Projects:/img/osgeo/osgeo-logo.png" */>}}
```

---

### `image-block-bar`

Renders a dark bar of image tiles with a title and subtitle beneath each image, one per positional title:subtitle:image-url argument.

Parameters: `0` — Positional args, each in the form title:subtitle:image-url (repeat for more tiles) · `animate` — true to add scroll animation classes (cannot be combined with positional args)

{{< image-block-bar "Software:Free geospatial tools:/img/osgeo/osgeo-logo.png" "Community:Global volunteer network:/img/osgeo/osgeo-logo.png" >}}

```text
{{</* image-block-bar "Software:Free geospatial tools:/img/osgeo/osgeo-logo.png" "Community:Global volunteer network:/img/osgeo/osgeo-logo.png" */>}}
```

---

### `image-block-section-bar`

Renders a dark section bar of image tiles with a colored title/subtitle panel beneath each image, one per positional title:subtitle:image-url:background-color argument.

Parameters: `0` — Positional args, each in the form title:subtitle:image-url:bulma-background-color (repeat for more tiles) · `animate` — true to add scroll animation classes (cannot be combined with positional args) · `backgroundColor` — Declared with default #FFF but not used in the output

{{< image-block-section-bar "Software:Free geospatial tools:/img/osgeo/osgeo-logo.png:primary" "Community:Global volunteer network:/img/osgeo/osgeo-logo.png:info" >}}

```text
{{</* image-block-section-bar "Software:Free geospatial tools:/img/osgeo/osgeo-logo.png:primary" "Community:Global volunteer network:/img/osgeo/osgeo-logo.png:info" */>}}
```

---

### `image-content-bar`

Renders a plain bar of small images with centered captions, one per positional caption:image-url argument.

Parameters: `0` — Positional args, each in the form caption:image-url (repeat for more tiles) · `animate` — true to add scroll animation classes (cannot be combined with positional args)

{{< image-content-bar "Open Source:/img/osgeo/osgeo-logo.png" "Open Data:/img/osgeo/osgeo-logo.png" >}}

```text
{{</* image-content-bar "Open Source:/img/osgeo/osgeo-logo.png" "Open Data:/img/osgeo/osgeo-logo.png" */>}}
```

---

### `img-grid`

Renders images in two tile rows (first two args on top, the rest below), one per positional label:image-url argument (only the URL part is used).

Parameters: `0` — Positional args, each in the form label:image-url; at least 3 required (first row uses args 1-2, second row args 3+) · `animate` — true to add scroll animation classes (cannot be combined with positional args)

{{< img-grid "a:/img/osgeo/osgeo-logo.png" "b:/img/osgeo/osgeo-logo.png" "c:/img/osgeo/osgeo-logo.png" "d:/img/osgeo/osgeo-logo.png" >}}

```text
{{</* img-grid "a:/img/osgeo/osgeo-logo.png" "b:/img/osgeo/osgeo-logo.png" "c:/img/osgeo/osgeo-logo.png" "d:/img/osgeo/osgeo-logo.png" */>}}
```

---

### `img-grid-1`

Renders a styled two-row image grid (first two args in the top row, remaining args in the bottom row), one image per positional label:image-url argument.

Parameters: `0` — Positional args, each in the form label:image-url (only the URL part is used) · `animate` — true to add scroll animation classes (cannot be combined with positional args)

{{< img-grid-1 "a:/img/osgeo/osgeo-logo.png" "b:/img/osgeo/osgeo-logo.png" "c:/img/osgeo/osgeo-logo.png" "d:/img/osgeo/osgeo-logo.png" >}}

```text
{{</* img-grid-1 "a:/img/osgeo/osgeo-logo.png" "b:/img/osgeo/osgeo-logo.png" "c:/img/osgeo/osgeo-logo.png" "d:/img/osgeo/osgeo-logo.png" */>}}
```

---

### `info-bar`

Renders a primary notification level bar of big statistic titles with small headings, one per positional title:heading argument.

Parameters: `0` — Positional args, each in the form big-text:small-heading (repeat for more items) · `animate` — true to add scroll animation classes (cannot be combined with positional args)

{{< info-bar "20+:Projects" "30k:Contributors" "1994:Founded" >}}

```text
{{</* info-bar "20+:Projects" "30k:Contributors" "1994:Founded" */>}}
```

---

### `info-card`

Renders a two-column card with an image on the left and a heading plus text on the right, inside a primary notification section.

Parameters: `0` — Image URL (positional) · `1` — Card heading (positional) · `2` — Card body text (positional) · `animate` — true to add scroll animation classes (cannot be combined with positional args)

{{< info-card "/img/osgeo/osgeo-logo.png" "About OSGeo" "OSGeo supports the collaborative development of open source geospatial software." >}}

```text
{{</* info-card "/img/osgeo/osgeo-logo.png" "About OSGeo" "OSGeo supports the collaborative development of open source geospatial software." */>}}
```

---

### `info-icons`

Renders a primary notification level bar of stacked Font Awesome icons with headings, one per positional heading:icon-class argument.

Parameters: `0` — Positional args, each in the form heading:fa-icon-class (repeat for more items) · `animate` — true to add scroll animation classes (cannot be combined with positional args)

{{< info-icons "Global:fa-globe" "Open:fa-unlock" "Community:fa-users" >}}

```text
{{</* info-icons "Global:fa-globe" "Open:fa-unlock" "Community:fa-users" */>}}
```

---

### `progress-bar`

Renders an indeterminate Bulma progress bar, optionally auto-hidden after a timeout.

Parameters: `autoHideAfter` — Milliseconds after which the bar is hidden via an inline script

{{< progress-bar autoHideAfter="3000" >}}

```text
{{</* progress-bar autoHideAfter="3000" */>}}
```

---

### `qrcode`

Renders a QR-code canvas for a URL (drawn client-side by the site's QR JS) with a Download button linking to the same URL.

Parameters: `0` — Target URL encoded in the QR code and used for the links (positional, default https://)

_This block depends on site data or external services and is not demoed inline._

```text
{{</* qrcode "https://www.osgeo.org/" */>}}
```

---

### `rich-list`

Renders a rich list tile (optionally a link) with icon or image, title, and subtitle; substitutes |version| and |ltrversion| placeholders from data/conf in the URL.

Parameters: `icon` — Optional Font Awesome icon class · `image` — Optional image URL shown in the tile · `layoutClass` — Layout/width CSS class (e.g. third) · `linkAttr` — Extra raw attribute string added to the anchor tag · `listLink` — Optional target URL; supports |version| and |ltrversion| placeholders · `listSubtitle` — Subtitle text of the tile · `listTitle` — Main title text of the tile

{{< rich-list layoutClass="third" icon="fas fa-book" listTitle="Documentation" listSubtitle="Read the project docs" listLink="https://www.osgeo.org/" >}}

```text
{{</* rich-list layoutClass="third" icon="fas fa-book" listTitle="Documentation" listSubtitle="Read the project docs" listLink="https://www.osgeo.org/" */>}}
```

---

### `spoiler-start`

Opens a collapsible spoiler block with a clickable label heading; close with spoiler-end wrapping the hidden content.

Parameters: `id` — Optional HTML id for the spoiler container · `title` — Spoiler label heading

{{< spoiler-start title="Show installation details" id="install-details" >}}
These are the **hidden details** revealed when the spoiler is opened.
{{< spoiler-end >}}

```text
{{</* spoiler-start title="Show installation details" id="install-details" */>}}
These are the **hidden details** revealed when the spoiler is opened.
{{</* spoiler-end */>}}
```

---

### `steps-bar`

Renders a numbered horizontal steps indicator with an icon and text per step, one per positional icon:text:is-active argument.

Parameters: `0` — Positional args, each in the form fa-icon-class:step-text:is-active (is-active true marks the active step) · `animate` — true to add scroll animation classes (cannot be combined with positional args)

{{< steps-bar "fas fa-download:Download the installer:true" "fas fa-cog:Run the setup wizard:false" "fas fa-map:Start mapping:false" >}}

```text
{{</* steps-bar "fas fa-download:Download the installer:true" "fas fa-cog:Run the setup wizard:false" "fas fa-map:Start mapping:false" */>}}
```

---

### `table`

Renders inner markdown containing a table as an accessible, scrollable data table with optional caption, custom class, and id.

Parameters: `class` — Extra CSS class(es) added to the table element · `id` — HTML id for the table (random digits when omitted) · `title` — Optional caption text; also enables schema.org Table markup

{{< table title="Board members" class="is-striped" id="board-table" >}}
| Name | Role |
| ---- | ---- |
| Alice Example | Chair |
| Bob Example | Treasurer |
{{< /table >}}

```text
{{</* table title="Board members" class="is-striped" id="board-table" */>}}
| Name | Role |
| ---- | ---- |
| Alice Example | Chair |
| Bob Example | Treasurer |
{{</* /table */>}}
```

---

### `tabs`

Renders a Bulma tabs header with up to five tab labels and inline JS that toggles matching tab-content blocks; substitutes |version| and |ltrversion| placeholders from data/conf.

Parameters: `tab1` — Label of tab 1 (initially active) · `tab2` — Label of tab 2 · `tab3` — Label of tab 3 · `tab4` — Label of tab 4 · `tab5` — Label of tab 5

{{< tabs tab1="Overview" tab2="Details" >}}
{{< tab-content-start tab="1" >}}
Overview content here.
{{< tab-content-end >}}
{{< tab-content-start tab="2" >}}
Detail content here.
{{< tab-content-end >}}

```text
{{</* tabs tab1="Overview" tab2="Details" */>}}
{{</* tab-content-start tab="1" */>}}
Overview content here.
{{</* tab-content-end */>}}
{{</* tab-content-start tab="2" */>}}
Detail content here.
{{</* tab-content-end */>}}
```

---

## Data blocks

### `blogroll`

Renders a numbered list of community blog posts from the headless /community-blogs page bundle filtered by showcase type.

Parameters: `showcase` — Showcase type to match against each blog resource's showcase front-matter param

_This block depends on site data or external services and is not demoed inline._

```text
{{</* blogroll showcase="planet" */>}}
```

---

### `commercial-support`

Renders a list of commercial support providers (logo, linked name, description) from a file under data/commercial_support.

Parameters: `dataFile` — Key of the data file under data/commercial_support to render

_This block depends on site data or external services and is not demoed inline._

```text
{{</* commercial-support dataFile="providers" */>}}
```

---

### `contributing-orgs`

Renders cards for contributing organizations from data/contributors, sorted by total commits, with thematic contribution badges and activity indicators.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* contributing-orgs */>}}
```

---

### `contribution-stats`

Renders a grid of statistic cards (organizations, individual contributors, commits, supporting contributors, Sol Katz recipients) computed from data/contributors.

Parameters: `0` — Which stats to show: all, orgs, individuals, commits, supporting, or sol-katz (default all) · `1` — Optional link URL applied to the stat cards

_This block depends on site data or external services and is not demoed inline._

```text
{{</* contribution-stats "all" "/community/contributors/" */>}}
```

---

### `donors`

Renders a sorted list of donor names from data/donors as rich-list tiles.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* donors */>}}
```

---

### `download-table`

Renders a static comparative pricing/download table (free, small business, teams, enterprise tiers) with donate/subscribe buttons linking into the download flow.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* download-table */>}}
```

---

### `flickr-images`

Renders a gallery of image tiles from the headless /flickr-images page bundle filtered by showcase type, with configurable column width.

Parameters: `columns` — Bulma column width number per tile, or 'gallery' for a mixed 4/6 layout (default 2) · `quantity` — Maximum number of images to show (default 100) · `showcase` — Showcase type to match against each image resource's showcase param

_This block depends on site data or external services and is not demoed inline._

```text
{{</* flickr-images showcase="community" quantity="6" columns="4" */>}}
```

---

### `flickr-images-old`

Legacy variant that renders numbered notification cards of Flickr images from the headless /flickr-images page bundle filtered by showcase type.

Parameters: `quantity` — Maximum number of resources considered (default 100) · `showcase` — Showcase type to match against each image resource's showcase param

_This block depends on site data or external services and is not demoed inline._

```text
{{</* flickr-images-old showcase="community" quantity="6" */>}}
```

---

### `fund`

Renders funder logo tiles grouped by level (Flagship, Large, Medium, Small) from the /funders page bundle or page-local funders resources, filtered to active, changelog, or past funders.

Parameters: `relativeImgPath` — If set, logo paths are used as-is instead of being prefixed with the funders/contributors image path · `type` — active (current funders), changelog (page-bundle funders/*md resources), or anything else for past funders

_This block depends on site data or external services and is not demoed inline._

```text
{{</* fund type="active" */>}}
```

---

### `funders-simple`

Renders the funders-simple partial, a simplified listing of funders from site data/pages.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* funders-simple */>}}
```

---

### `individual-contributors`

Renders ranked cards for individual GitHub contributors from data/contributors, with avatars, honorary-member badges, commit counts, and thematic badges.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* individual-contributors */>}}
```

---

### `linux-packages-explorer`

Renders a JavaScript file-tree explorer for Linux package downloads of a given distribution from data/downloads/linux_packages.

Parameters: `distribution` — Distribution key (dashes mapped to underscores) matching a file under data/downloads/linux_packages

_This block depends on site data or external services and is not demoed inline._

```text
{{</* linux-packages-explorer distribution="debian" */>}}
```

---

### `param`

Prints the value of a key from data/conf as plain text.

Parameters: `0` — Key in data/conf to print (positional)

_This block depends on site data or external services and is not demoed inline._

```text
{{</* param "version" */>}}
```

---

### `param-link`

Prints the value of a key from data/conf rendered through markdownify (so markdown links become anchors).

Parameters: `0` — Key in data/conf to render as markdown (positional)

_This block depends on site data or external services and is not demoed inline._

```text
{{</* param-link "download_link" */>}}
```

---

### `payrexx-widget`

Renders a Payrexx donation widget with one-time/monthly amount pickers built from data/payrexx_products, currency selector, and optional skip/hide buttons.

Parameters: `alreadyDonated` — If set, shows a button to hide the donate prompt · `otherMethods` — If set, shows a link to other donation methods · `skipToDownload` — If set, shows a button to skip donating and go to download

_This block depends on site data or external services and is not demoed inline._

```text
{{</* payrexx-widget otherMethods="true" skipToDownload="true" */>}}
```

---

### `s3-file-explorer`

Renders a searchable, sortable JavaScript file-tree explorer over the S3 downloads tree from data/downloads/s3_downloads.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* s3-file-explorer */>}}
```

---

### `shortcodes`

Renders a thumbnail grid linking to every page under the docs/shortcodes/ section of the site.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* shortcodes */>}}
```

---

### `sol-katz-award`

Renders Sol Katz Award recipient cards (name, year badge, citation, description, links, photo) from data/contributors, newest first.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* sol-katz-award */>}}
```

---

### `stripe-widget`

Renders a Stripe donation widget with one-time/monthly amount pickers built from data/stripe_products, currency selector, and optional skip/hide buttons.

Parameters: `alreadyDonated` — If set, shows a button to hide the donate prompt · `otherMethods` — If set, shows a link to other donation methods · `skipToDownload` — If set, shows a button to skip donating and go to download

_This block depends on site data or external services and is not demoed inline._

```text
{{</* stripe-widget otherMethods="true" alreadyDonated="true" */>}}
```

---

### `supporting-contributors`

Renders supporting-contributor cards from data/contributors, split into Organizations and Individuals sections sorted by start date, with role badges.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* supporting-contributors */>}}
```

---

### `usecase`

Renders the usecase partial for the first case-study page found in the project section.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* usecase */>}}
```

---

### `usecases`

Renders featured case studies as a JS carousel plus a grid of active case studies and a link to the archive, from project-section case-study pages.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* usecases */>}}
```

---

### `usecases-archive`

Renders a grid of archived case-study pages from the project section, newest first.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* usecases-archive */>}}
```

---

### `visualchangelogs`

Renders a linked list of visual-changelog pages in the project section sorted by release date, newest first.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* visualchangelogs */>}}
```

---

## Utility blocks

### `footnote`

Renders a bracketed numbered self-anchor link like [1] usable as a footnote marker.

Parameters: `0` — Footnote number used for the anchor id and label (positional)

{{< footnote "1" >}}

```text
{{</* footnote "1" */>}}
```

---

### `language-select`

Renders a language dropdown built from the site's lang menu and JS that rewrites link-with-language URLs when the selection changes.

_This block depends on site data or external services and is not demoed inline._

```text
{{</* language-select */>}}
```

---

### `rich-edit-on-gh`

Renders a rich-list tile linking to the current page's GitHub edit URL, inviting readers to submit a PR.

Parameters: `layoutClass` — Layout/width CSS class added to the tile

{{< rich-edit-on-gh layoutClass="third" >}}

```text
{{</* rich-edit-on-gh layoutClass="third" */>}}
```

---

### `script`

Emits a deferred script tag for a JavaScript asset resolved from site assets via resources.Get.

Parameters: `src` — Asset path of the JavaScript file (relative to assets/)

_This block depends on site data or external services and is not demoed inline._

```text
{{</* script src="js/carousel.js" */>}}
```

---

### `table-of-contents`

Renders the current page's Hugo-generated table of contents.

{{< table-of-contents >}}

```text
{{</* table-of-contents */>}}
```

---

### `yeartag`

Prints the current year at build time.

{{< yeartag >}}

```text
{{</* yeartag */>}}
```

---

