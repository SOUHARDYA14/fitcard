// FitCard — shared editorial theme behaviors:
// custom cursor, scroll-reveal, magnetic buttons.
(function(){
  const isCoarse = window.matchMedia("(pointer:coarse)").matches;

  // ---- Custom cursor (dot snaps instantly, ring eases behind) ----
  if (!isCoarse) {
    const dot = document.createElement("div");
    dot.className = "cursor-dot";
    const ring = document.createElement("div");
    ring.className = "cursor-ring";
    document.body.append(dot, ring);

    let mx = window.innerWidth / 2, my = window.innerHeight / 2;
    let rx = mx, ry = my;
    window.addEventListener("mousemove", (e) => {
      mx = e.clientX; my = e.clientY;
      dot.style.transform = `translate(${mx}px, ${my}px) translate(-50%,-50%)`;
    });
    (function loop(){
      rx += (mx - rx) * 0.18;
      ry += (my - ry) * 0.18;
      ring.style.transform = `translate(${rx}px, ${ry}px) translate(-50%,-50%)`;
      requestAnimationFrame(loop);
    })();

    document.addEventListener("mouseover", (e) => {
      if (e.target.closest("a, button, input, select, .magnetic, .cc, .row")) {
        ring.classList.add("hover");
      }
    });
    document.addEventListener("mouseout", (e) => {
      if (e.target.closest("a, button, input, select, .magnetic, .cc, .row")) {
        ring.classList.remove("hover");
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
