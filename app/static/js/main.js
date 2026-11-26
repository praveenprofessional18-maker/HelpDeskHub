"use strict";

function setFieldError(form, field, message) {
  const error = form.querySelector(`[data-error-for="${field.name}"]`);
  if (!error) return;
  error.textContent = message;
  field.setAttribute("aria-invalid", message ? "true" : "false");
}
