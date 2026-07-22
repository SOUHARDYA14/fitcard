// FitCard — shared editorial theme behaviors:
// custom cursor, scroll-reveal, magnetic buttons.
(function(){
  const isCoarse = window.matchMedia("(pointer:coarse)").matches;

  // ---- Custom cursor (crosshair, snaps instantly to the pointer) ----
  if (!isCoarse) {
    const crosshair = document.createElement("div");
    crosshair.className = "cursor-crosshair";
    const hLine = document.createElement("span");
    hLine.className = "h-line";
    const vLine = document.createElement("span");
    vLine.className = "v-line";
    crosshair.append(hLine, vLine);
    document.body.append(crosshair);

    window.addEventListener("mousemove", (e) => {
      crosshair.style.transform = `translate(${e.clientX}px, ${e.clientY}px) translate(-50%,-50%)`;
    });

    document.addEventListener("mouseover", (e) => {
      if (e.target.closest("a, button, input, select, .magnetic, .cc, .row")) {
        crosshair.classList.add("hover");
      }
    });
    document.addEventListener("mouseout", (e) => {
      if (e.target.closest("a, button, input, select, .magnetic, .cc, .row")) {
        crosshair.classList.remove("hover");
      }
    });
  }

  // ---- Scroll reveal ----
  const revealEls = document.querySelectorAll(".reveal");
  if (revealEls.length) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          io.unobserve(entry.target);
        }
      });
    }, { threshold: 0.15 });
    revealEls.forEach(el => io.observe(el));
  }

  // ---- Magnetic buttons ----
  if (!isCoarse) {
    document.querySelectorAll(".magnetic").forEach(el => {
      el.addEventListener("mousemove", (e) => {
        const rect = el.getBoundingClientRect();
        const dx = e.clientX - (rect.left + rect.width / 2);
        const dy = e.clientY - (rect.top + rect.height / 2);
        el.style.transform = `translate(${dx * 0.25}px, ${dy * 0.35}px)`;
      });
      el.addEventListener("mouseleave", () => {
        el.style.transform = "translate(0,0)";
      });
    });
  }
})();
