(function () {
  var page = document.body.getAttribute("data-page");
  var navLinks = document.querySelectorAll("[data-nav]");
  var navToggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav-menu]");
  var topButton = document.querySelector("[data-back-to-top]");
  var copyButton = document.querySelector("[data-copy-citation]");

  navLinks.forEach(function (link) {
    if (link.getAttribute("data-nav") === page) {
      link.classList.add("is-active");
      link.setAttribute("aria-current", "page");
    }
  });

  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(open));
    });
  }

  if (topButton) {
    window.addEventListener("scroll", function () {
      topButton.classList.toggle("is-visible", window.scrollY > 540);
    });

    topButton.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }

  if (copyButton) {
    copyButton.addEventListener("click", function () {
      var target = document.querySelector(copyButton.getAttribute("data-copy-citation"));
      if (!target) return;

      var markCopied = function () {
        copyButton.innerText = "Copied";
        window.setTimeout(function () {
          copyButton.innerText = "Copy";
        }, 1400);
      };

      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(target.innerText).then(markCopied);
        return;
      }

      var textArea = document.createElement("textarea");
      textArea.value = target.innerText;
      textArea.setAttribute("readonly", "");
      textArea.style.position = "fixed";
      textArea.style.left = "-9999px";
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand("copy");
      document.body.removeChild(textArea);
      markCopied();
    });
  }
})();
