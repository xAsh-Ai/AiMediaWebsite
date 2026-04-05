document.documentElement.classList.add("js-ready");

const normalizePathname = (pathname) => {
  if (!pathname || pathname === "/") {
    return "/index.html";
  }

  if (pathname.endsWith("/")) {
    return `${pathname}index.html`;
  }

  const lastSegment = pathname.split("/").pop();

  if (lastSegment && !lastSegment.includes(".")) {
    return `${pathname}/index.html`;
  }

  return pathname;
};

const navToggle = document.querySelector("[data-nav-toggle]");
const siteNav = document.querySelector("[data-site-nav]");
const currentPath = normalizePathname(window.location.pathname);

document.querySelectorAll(".site-nav a").forEach((link) => {
  const linkPath = normalizePathname(new URL(link.href, window.location.origin).pathname);

  if (linkPath === currentPath) {
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
const showRevealItems = () => revealItems.forEach((item) => item.classList.add("is-visible"));
const canUseRevealObserver =
  revealItems.length > 0 &&
  !window.matchMedia("(prefers-reduced-motion: reduce)").matches &&
  "IntersectionObserver" in window;

if (canUseRevealObserver) {
  try {
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
  } catch (error) {
    showRevealItems();
  }
} else {
  showRevealItems();
}
