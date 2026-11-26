document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector("#sidebar");
  const menuToggle = document.querySelector(".menu-toggle");
  if (menuToggle && sidebar) {
    menuToggle.addEventListener("click", () => {
      const open = sidebar.classList.toggle("open");
      menuToggle.setAttribute("aria-expanded", String(open));
    });
  }

  document.querySelectorAll(".toast-close").forEach((button) => {
    button.addEventListener("click", () => {
      const toast = button.closest(".toast");
      toast.classList.add("leaving");
      setTimeout(() => toast.remove(), 220);
    });
  });
  document.querySelectorAll(".toast").forEach((toast) => {
    setTimeout(() => {
      if (toast.isConnected) {
        toast.classList.add("leaving");
        setTimeout(() => toast.remove(), 220);
      }
    }, 5000);
  });

  document.querySelectorAll(".password-toggle").forEach((button) => {
    button.addEventListener("click", () => {
      const input = button.parentElement.querySelector("input");
      const show = input.type === "password";
      input.type = show ? "text" : "password";
      button.textContent = show ? "Hide" : "Show";
    });
  });

  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      let valid = true;
      form.querySelectorAll("[required]").forEach((field) => {
        if (!field.checkValidity()) {
          valid = false;
          field.classList.add("invalid");
        } else {
          field.classList.remove("invalid");
        }
      });
      if (!valid) return;
      const submit = form.querySelector('button[type="submit"]');
      if (submit) {
        submit.disabled = true;
        submit.dataset.originalText = submit.textContent;
        submit.textContent = "Please wait...";
        setTimeout(() => {
          submit.disabled = false;
          submit.textContent = submit.dataset.originalText;
        }, 3000);
      }
    });
  });

  const revealObserver = "IntersectionObserver" in window
    ? new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            revealObserver.unobserve(entry.target);
          }
        });
      }, { threshold: 0.12 })
    : null;
  document.querySelectorAll(".reveal").forEach((element) => {
    if (revealObserver) revealObserver.observe(element);
    else element.classList.add("visible");
  });

  document.querySelectorAll("[data-count]").forEach((element) => {
    const target = Number(element.dataset.count);
    const duration = 550;
    const start = performance.now();
    const update = (now) => {
      const progress = Math.min((now - start) / duration, 1);
      element.textContent = Math.round(target * (1 - Math.pow(1 - progress, 3)));
      if (progress < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  });
});
