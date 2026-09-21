document.addEventListener("DOMContentLoaded", () => {
  // Navbar scroll effect
  const nav = document.querySelector(".cs-navbar");
  if (nav) {
    const onScroll = () => {
      nav.classList.toggle("scrolled", window.scrollY > 12);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    onScroll();
  }

  // Auto-dismiss alerts
  document.querySelectorAll(".alert-dismissible").forEach((el) => {
    setTimeout(() => {
      const btn = el.querySelector(".btn-close");
      if (btn) btn.click();
    }, 4500);
  });

  // Quantity steppers
  document.querySelectorAll("[data-qty-step]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const input = document.querySelector(btn.dataset.qtyStep);
      if (!input) return;
      let v = parseInt(input.value || "1", 10);
      const delta = parseInt(btn.dataset.delta || "0", 10);
      v = Math.max(1, v + delta);
      input.value = v;
    });
  });
});
