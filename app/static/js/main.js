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
