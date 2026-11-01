const SECTION_ACHIEVEMENTS = {
  about: ["First Steps", "You entered the Stone biome."],
  skills: ["Full Inventory", "You explored the tools in your loadout."],
  projects: ["Builder's Guild", "You discovered the project cavern."],
  certifications: ["Treasure Hunter", "You found the certificate loot."],
  contact: ["Reached Bedrock", "You made it to the deepest layer. Say hello!"],
};

class ContactForm {
  constructor(form) {
    this.form = form;
    this.submitButton = form.querySelector('button[type="submit"]');
    this.submitLabel = form.querySelector(".submit-label");
    this.status = document.querySelector("#form-status");
    form.addEventListener("submit", (event) => this.submit(event));
  }

  async submit(event) {
    event.preventDefault();
    this.status.textContent = "";
    this.status.classList.remove("is-error");

    if (!this.form.reportValidity()) {
      return;
    }

    const formData = new FormData(this.form);
    const payload = Object.fromEntries(formData.entries());
    this.setLoading(true);

    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: AbortSignal.timeout(15000),
      });
      let result;
      try {
        result = await response.json();
      } catch {
        throw new Error("The server returned an invalid response. Please try again later.");
      }

      if (!response.ok || result.ok !== true) {
        throw new Error(result.error || "Your message could not be sent. Please try again.");
      }

      this.form.reset();
      this.status.textContent = "Thanks for reaching out! Your message has been received.";
    } catch (error) {
      this.status.classList.add("is-error");
      this.status.textContent =
        error.name === "TimeoutError"
          ? "The request timed out. Please check your connection and try again."
          : error instanceof TypeError
            ? "Couldn't reach the contact service. Please try again in a moment."
            : error.message;
    } finally {
      this.setLoading(false);
    }
  }

  setLoading(isLoading) {
    this.submitButton.disabled = isLoading;
    this.submitButton.setAttribute("aria-busy", String(isLoading));
    this.submitLabel.textContent = isLoading ? "Sending…" : "Send message";
  }
}

class GitHubProfile {
  constructor(username, status, indicator) {
    this.username = username;
    this.status = status;
    this.indicator = indicator;
  }

  async load() {
    try {
      const response = await fetch(`https://api.github.com/users/${this.username}`, {
        headers: { Accept: "application/vnd.github+json" },
        signal: AbortSignal.timeout(10000),
      });

      if (!response.ok) {
        throw new Error(`GitHub profile request failed (${response.status}).`);
      }

      const profile = await response.json();
      if (!Number.isInteger(profile.public_repos) || !Number.isInteger(profile.followers)) {
        throw new Error("GitHub profile response is incomplete.");
      }

      this.status.textContent =
        `${profile.public_repos} public repositories · ${profile.followers} followers on GitHub.`;
      this.indicator.classList.add("is-connected");
    } catch {
      this.status.textContent = "GitHub stats unavailable right now. You can still visit my profile.";
    }
  }
}

class SectionNavigation {
  constructor(sections, links) {
    this.links = links;
    this.activeSection = null;
    this.observer = new IntersectionObserver(
      (entries) => {
        const visibleSection = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (visibleSection) {
          this.setActiveSection(visibleSection.target.id);
        }
      },
      { rootMargin: "-15% 0px -70% 0px", threshold: [0, 0.1, 0.25] },
    );

    sections.forEach((section) => this.observer.observe(section));
  }

  setActiveSection(sectionId) {
    if (sectionId === this.activeSection) {
      return;
    }

    this.activeSection = sectionId;
    this.links.forEach((link) => {
      if (link.hash === `#${sectionId}`) {
        link.setAttribute("aria-current", "location");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }
}

class WorldExplorer {
  constructor(sections) {
    this.sections = sections;
    this.activeSection = sections[0] ?? null;
    this.discovered = new Set();
    this.depthCoordinate = document.querySelector("#depth-coordinate");
    this.depthLayer = document.querySelector("#depth-layer");
    this.depthFill = document.querySelector(".depth-fill");
    this.discovery = document.querySelector("#discovery");
    this.achievementTitle = document.querySelector("#achievement-title");
    this.achievementDescription = document.querySelector("#achievement-description");
    this.discoveryTimeout = null;
    this.onScroll = () => this.updateDepth();

    this.observer = new IntersectionObserver(
      (entries) => {
        const visibleSection = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

        if (visibleSection) {
          this.setActiveSection(visibleSection.target);
        }
      },
      { rootMargin: "-30% 0px -55% 0px", threshold: [0, 0.1, 0.25] },
    );

    sections.forEach((section) => this.observer.observe(section));
    window.addEventListener("scroll", this.onScroll, { passive: true });
    window.addEventListener("resize", this.onScroll);
    this.updateDepth();
    this.setActiveSection(this.activeSection, false);
  }

  setActiveSection(section, notify = true) {
    if (!section) {
      return;
    }

    this.activeSection = section;
    this.depthLayer.textContent = section.dataset.layer;

    if (!notify || section.id === "home" || this.discovered.has(section.id)) {
      return;
    }

    this.discovered.add(section.id);
    const [title, description] = SECTION_ACHIEVEMENTS[section.id] ?? [
      `${section.dataset.layer} Discovered`,
      "You uncovered a new area.",
    ];
    this.achievementTitle.textContent = title;
    this.achievementDescription.textContent = description;
    this.discovery.classList.add("is-visible");
    window.clearTimeout(this.discoveryTimeout);
    this.discoveryTimeout = window.setTimeout(() => {
      this.discovery.classList.remove("is-visible");
    }, 3400);
  }

  updateDepth() {
    const scrollableHeight = document.documentElement.scrollHeight - window.innerHeight;
    const progress = scrollableHeight > 0 ? window.scrollY / scrollableHeight : 0;
    this.depthCoordinate.textContent = `Y ${Math.round(64 - progress * 448)}`;
    this.depthFill.style.height = `${Math.min(100, Math.max(0, progress * 100))}%`;
  }
}

class DiscordProjectSlideshow {
  constructor(container) {
    this.slides = [...container.querySelectorAll("[data-slide]")];
    this.dots = [...container.querySelectorAll("[data-slide-index]")];
    this.status = container.querySelector("[data-slide-status]");
    this.activeIndex = 0;

    container.querySelectorAll("[data-slide-direction]").forEach((button) => {
      button.addEventListener("click", () => {
        this.show(this.activeIndex + Number(button.dataset.slideDirection));
      });
    });

    this.dots.forEach((button) => {
      button.addEventListener("click", () => {
        this.show(Number(button.dataset.slideIndex));
      });
    });

    this.show(this.activeIndex);
  }

  show(index) {
    this.activeIndex = (index + this.slides.length) % this.slides.length;
    this.slides.forEach((slide, slideIndex) => {
      const isActive = slideIndex === this.activeIndex;
      slide.hidden = !isActive;
      slide.setAttribute("aria-hidden", String(!isActive));
      this.dots[slideIndex].setAttribute("aria-current", String(isActive));
    });

    const slideName = this.slides[this.activeIndex].getAttribute("aria-label").replace(/^\d+ of \d+: /, "");
    this.status.textContent = `${this.activeIndex + 1} / ${this.slides.length} — ${slideName}`;
  }
}

class MinecartContactJourney {
  constructor(links, contact, ride, status) {
    this.links = links;
    this.contact = contact;
    this.heading = contact.querySelector("#contact-title");
    this.ride = ride;
    this.status = status;
    this.isTraveling = false;
    this.prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    links.forEach((link) => {
      link.addEventListener("click", (event) => this.start(event));
    });
  }

  start(event) {
    event.preventDefault();
    if (this.isTraveling) {
      return;
    }

    this.isTraveling = true;
    this.status.textContent = this.prefersReducedMotion.matches
      ? "Opening the contact section."
      : "Minecart departing for the contact section.";

    if (this.prefersReducedMotion.matches) {
      this.arrive();
      return;
    }

    this.ride.classList.add("is-moving");
    window.setTimeout(() => this.arrive(), 1550);
  }

  arrive() {
    this.ride.classList.remove("is-moving");
    window.history.pushState(null, "", "#contact");
    this.contact.scrollIntoView({
      behavior: this.prefersReducedMotion.matches ? "instant" : "smooth",
      block: "start",
    });
    this.heading.focus({ preventScroll: true });
    this.status.textContent = "Arrived. The contact form and profiles are ready below.";
    this.isTraveling = false;
  }
}

class PortfolioApp {
  constructor() {
    const contactForm = document.querySelector("#contact-form");
    if (contactForm) {
      new ContactForm(contactForm);
    }

    const githubStatus = document.querySelector("#github-stats-text");
    const githubIndicator = document.querySelector(".github-indicator");
    if (githubStatus && githubIndicator) {
      new GitHubProfile("Galaxy17isCrying", githubStatus, githubIndicator).load();
    }

    const navigationLinks = [...document.querySelectorAll(".site-nav a")];
    const observedSections = navigationLinks
      .map((link) => document.querySelector(link.hash))
      .filter(Boolean);

    if (observedSections.length > 0 && "IntersectionObserver" in window) {
      new SectionNavigation(observedSections, navigationLinks);
    }

    const worldSections = [...document.querySelectorAll(".world-hero[data-layer], .world-section[data-layer]")];
    if (worldSections.length > 0 && "IntersectionObserver" in window) {
      new WorldExplorer(worldSections);
    }

    document.querySelectorAll("[data-project-slideshow]").forEach((slideshow) => {
      new DiscordProjectSlideshow(slideshow);
    });

    const contactLinks = [...document.querySelectorAll("[data-contact-journey]")];
    const contactSection = document.querySelector("#contact");
    const minecartRide = document.querySelector("#minecart-journey");
    const journeyStatus = document.querySelector("#journey-status");
    if (contactLinks.length > 0 && contactSection && minecartRide && journeyStatus) {
      new MinecartContactJourney(contactLinks, contactSection, minecartRide, journeyStatus);
    }
  }
}

document.addEventListener("DOMContentLoaded", () => new PortfolioApp());
