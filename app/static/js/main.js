"use strict";

function setFieldError(form, field, message) {
  const error = form.querySelector(`[data-error-for="${field.name}"]`);
  if (!error) return;
  error.textContent = message;
  field.setAttribute("aria-invalid", message ? "true" : "false");
}

function validateForm(form) {
  let valid = true;
  const fields = Array.from(form.querySelectorAll("input, select, textarea"))
    .filter((field) => field.type !== "hidden");

  fields.forEach((field) => {
    let message = "";
    if (!field.value.trim()) {
      message = "This field is required.";
    } else if (field.type === "email" && !field.validity.valid) {
      message = "Enter a valid email address.";
    } else if (field.type === "password" && field.value.length < 8) {
      message = "Password must be at least 8 characters.";
    }
    setFieldError(form, field, message);
    if (message) valid = false;
  });

  const password = form.elements.namedItem("password");
  const confirmation = form.elements.namedItem("confirm_password");
  if (password && confirmation && confirmation.value && password.value !== confirmation.value) {
    setFieldError(form, confirmation, "Passwords do not match.");
    valid = false;
  }
  return valid;
}

function initValidation() {
  document.querySelectorAll("form[data-validate]").forEach((form) => {
    form.addEventListener("input", (event) => {
      if (event.target.matches("input, select, textarea")) {
        setFieldError(form, event.target, "");
      }
    });

    form.addEventListener("submit", (event) => {
      if (validateForm(form)) return;
      event.preventDefault();
      const firstInvalid = form.querySelector('[aria-invalid="true"]');
      if (firstInvalid) firstInvalid.focus();
    });
  });
}

function initAdminFilters() {
  const controls = document.querySelector("[data-filters]");
  const cards = Array.from(document.querySelectorAll("[data-ticket-card]"));
  if (!controls || cards.length === 0) return;

  const search = controls.querySelector('[data-filter="search"]');
  const status = controls.querySelector('[data-filter="status"]');
  const category = controls.querySelector('[data-filter="category"]');
  const priority = controls.querySelector('[data-filter="priority"]');
  const results = document.querySelector("[data-results-count]");
  const emptyState = document.querySelector("[data-admin-empty]");

  function filterCards() {
    const term = search.value.trim().toLowerCase();
    let visibleCount = 0;
    cards.forEach((card) => {
      const matchesSearch = `${card.dataset.id} ${card.dataset.title}`.toLowerCase().includes(term);
      const matchesStatus = !status.value || card.dataset.status === status.value;
      const matchesCategory = !category.value || card.dataset.category === category.value;
      const matchesPriority = !priority.value || card.dataset.priority === priority.value;
      const visible = matchesSearch && matchesStatus && matchesCategory && matchesPriority;
      card.hidden = !visible;
      if (visible) visibleCount += 1;
    });
    results.textContent = `${visibleCount} matching tickets`;
    emptyState.hidden = visibleCount > 0;
  }

  controls.addEventListener("input", filterCards);
  controls.addEventListener("change", filterCards);
  const applyButton = controls.querySelector("[data-apply-filters]");
  applyButton.addEventListener("click", () => {
    const params = new URLSearchParams();
    if (status.value) params.set("status", status.value);
    if (category.value) params.set("category", category.value);
    if (priority.value) params.set("priority", priority.value);
    if (search.value.trim()) params.set("search", search.value.trim());
    window.location.assign(`${window.location.pathname}?${params.toString()}`);
  });

  search.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      applyButton.click();
    }
  });
  filterCards();
}

document.addEventListener("DOMContentLoaded", () => {
  initValidation();
  initAdminFilters();
});
