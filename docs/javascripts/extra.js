/* Extra JS for Hacking Notes.
 *
 * Forces every sidebar section to start collapsed. Material's `instant`
 * navigation and the auto-expansion of the active section can leave
 * the sidebar in a state where several sections are open at once; this
 * snippet normalises that on every page load.
 */
(function () {
  function collapseAllSections() {
    var toggles = document.querySelectorAll(
      ".md-nav__item--section.md-nav__item--nested > .md-nav__toggle"
    );
    toggles.forEach(function (t) {
      t.checked = false;
    });
  }

  // Run on initial page load
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", collapseAllSections);
  } else {
    collapseAllSections();
  }

  // And after every `instant` navigation
  if (typeof window.document$ !== "undefined" && window.document$.subscribe) {
    window.document$.subscribe(collapseAllSections);
  }
})();
