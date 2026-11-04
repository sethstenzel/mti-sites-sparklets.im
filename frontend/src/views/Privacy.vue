<template>
  <article class="privacy">
    <header>
      <h1>Privacy policy</h1>
      <p class="updated">Last updated November 4, 2026</p>
    </header>

    <section class="short">
      <h2>The short version</h2>
      <ul>
        <li>No accounts, no ads, no analytics, no tracking cookies. We don’t sell anything about you.</li>
        <li>A sparklet is the photo, names, message and style you choose. That’s all we store about it.</li>
        <li>Anyone with a sparklet’s link can open it, so share the link only with the person it’s for.</li>
        <li>Photos are resized and stripped of hidden data such as camera details and GPS location.</li>
        <li>Want a sparklet deleted? Email <a :href="`mailto:${CONTACT}`">{{ CONTACT }}</a> with its link.</li>
      </ul>
    </section>

    <section>
      <h2>What a sparklet contains</h2>
      <p>
        When you create a sparklet we store what you put on the card: the “To” and “From” names, your
        message, your photo, and the look you picked (colors, font, tilt and entrance animation), plus
        the time it was created or last edited. We don’t ask for your name, email address or phone
        number, and we don’t create an account for you.
      </p>
    </section>

    <section>
      <h2>Who can see a sparklet</h2>
      <p>
        Each sparklet gets a long, random link (for example <code>sparklets.im/s/…</code>) that can’t be
        guessed. Anyone who has the link or scans its QR code can open the sparklet, so treat it like a
        private note and share it only with the people it’s meant for.
      </p>
      <p>
        When a link is pasted into a chat app or social network, that service may show a preview. The
        preview is always generic (“You’ve got a sparklet”): it never shows the photo, the names or the
        message. We also ask search engines not to list sparklet pages.
      </p>
    </section>

    <section>
      <h2>Photos</h2>
      <p>
        Your photo is cropped in your browser, then resized and saved as a JPEG on our server. This
        removes hidden information that photos often carry, such as the camera model and the location
        where the picture was taken. If two people upload exactly the same picture, it’s stored once and
        shared. Please only upload photos you have the right to share.
      </p>
    </section>

    <section>
      <h2>Information collected automatically</h2>
      <p>
        Like most websites, our web server keeps standard access logs: your IP address, browser type,
        the pages requested and the time. We use them only to keep the site running and to stop abuse
        (for example, limiting how quickly sparklets can be created). They are deleted automatically
        after about two weeks.
      </p>
    </section>

    <section>
      <h2>Stored on your device</h2>
      <p>
        We don’t use cookies. Your browser’s local storage remembers the site theme you choose (Neutral,
        Blush or Slate) so the site looks the same next time. Site administrators also have their admin
        key stored this way. You can clear this at any time in your browser settings.
      </p>
    </section>

    <section>
      <h2>Other services</h2>
      <ul>
        <li>
          <strong>Hosting.</strong> Sparklets run on a cloud server provided by Akamai (Linode), which
          stores the data on our behalf.
        </li>
        <li>
          <strong>Fonts.</strong> The site’s fonts are loaded from Google Fonts, so your browser connects
          to Google’s servers when a page loads. See
          <a href="https://policies.google.com/privacy" target="_blank" rel="noopener">Google’s privacy policy</a>.
        </li>
        <li>
          <strong>Sharing.</strong> QR codes are made in your browser. The Facebook, Messenger, X and Email
          buttons only do something when you click them; at that point you’re using that service, under
          its own privacy policy. Email sharing happens entirely in your own email app.
        </li>
      </ul>
    </section>

    <section>
      <h2>How long we keep things</h2>
      <p>
        Sparklets are kept until they’re deleted. Server logs are deleted after about two weeks. Backup
        copies made when we update the site are deleted after 30 days, so a deleted sparklet may remain
        in a backup for up to 30 days.
      </p>
    </section>

    <section>
      <h2>Deleting a sparklet</h2>
      <p>
        Email <a :href="`mailto:${CONTACT}`">{{ CONTACT }}</a> with the sparklet’s link and we’ll delete
        it along with its photo. Because there are no accounts, anyone with the link can ask, so please
        let us know if you’re the sender or the recipient.
      </p>
    </section>

    <section>
      <h2>Children</h2>
      <p>
        Sparklets isn’t directed at children under 13, and we don’t knowingly collect personal
        information from them. A parent or guardian who wants a sparklet removed can email us with its
        link.
      </p>
    </section>

    <section>
      <h2>Changes to this policy</h2>
      <p>
        If we change how Sparklets handles information, we’ll update this page and the date at the top.
      </p>
    </section>

    <section>
      <h2>Contact</h2>
      <p>Questions about privacy: <a :href="`mailto:${CONTACT}`">{{ CONTACT }}</a></p>
    </section>
  </article>
</template>

<script setup>
const CONTACT = 'privacy@sparklets.im'
</script>

<style scoped>
.privacy {
  max-width: 44rem;
  margin: 0 auto;
  padding: 2.5rem 1.25rem 4rem;
  color: var(--ink);
}

h1 {
  font-size: clamp(2rem, 5vw, 2.8rem);
  font-weight: 800;
  letter-spacing: -0.035em;
  line-height: 1.05;
}

.updated {
  margin-top: 0.5rem;
  color: var(--ink-3);
  font-size: 0.925rem;
}

section {
  margin-top: 2.25rem;
}

h2 {
  margin-bottom: 0.6rem;
  font-size: 1.25rem;
  font-weight: 750;
  letter-spacing: -0.02em;
}

p,
li {
  color: var(--ink-2);
  font-size: 1.02rem;
  line-height: 1.65;
}

p + p {
  margin-top: 0.8rem;
}

ul {
  display: grid;
  gap: 0.55rem;
  padding-left: 1.2rem;
}

strong {
  color: var(--ink);
}

a {
  color: var(--ink);
  text-decoration-color: color-mix(in srgb, var(--ink) 35%, transparent);
  text-underline-offset: 3px;
}

a:hover {
  text-decoration-color: currentColor;
}

code {
  padding: 0.1em 0.35em;
  border-radius: 6px;
  background: var(--surface-2);
  font-size: 0.9em;
}

.short {
  margin-top: 1.75rem;
  padding: 1.25rem 1.4rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: var(--surface);
}

.short ul {
  padding-left: 1.1rem;
}
</style>
