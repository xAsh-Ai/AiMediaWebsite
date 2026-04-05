document.documentElement.classList.add("js-ready");

const navToggle = document.querySelector("[data-nav-toggle]");
const siteNav = document.querySelector("[data-site-nav]");
const currentPath = window.location.pathname.replace(/\/$/, "") || "/index.html";

document.querySelectorAll(".site-nav a").forEach((link) => {
  const linkPath = new URL(link.href, window.location.origin).pathname.replace(/\/$/, "");

  if (linkPath === currentPath || (currentPath === "" && linkPath === "/index.html")) {
    link.setAttribute("aria-current", "page");
  }
});

if (navToggle && siteNav) {
  navToggle.addEventListener("click", () => {
    const expanded = navToggle.getAttribute("aria-expanded") === "true";

    navToggle.setAttribute("aria-expanded", String(!expanded));
    siteNav.classList.toggle("is-open", !expanded);
  });
}

const revealItems = document.querySelectorAll(".reveal");

if (!window.matchMedia("(prefers-reduced-motion: reduce)").matches && revealItems.length > 0) {
  const revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          revealObserver.unobserve(entry.target);
        }
      });
    },
    {
      threshold: 0.15,
      rootMargin: "0px 0px -10% 0px",
    },
  );

  revealItems.forEach((item) => revealObserver.observe(item));
} else {
  revealItems.forEach((item) => item.classList.add("is-visible"));
}
