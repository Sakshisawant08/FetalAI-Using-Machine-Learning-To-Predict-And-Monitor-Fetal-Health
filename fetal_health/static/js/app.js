document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.querySelector("[data-theme-toggle]");
    const savedTheme = localStorage.getItem("fetal-health-theme");
    const systemPrefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;

    const applyTheme = (theme) => {
        const dark = theme === "dark";
        document.body.classList.toggle("dark-mode", dark);

        if (themeToggle) {
            themeToggle.innerHTML = dark
                ? '<i class="bi bi-sun-fill"></i>'
                : '<i class="bi bi-moon-stars-fill"></i>';
            themeToggle.setAttribute("aria-label", dark ? "Switch to light mode" : "Switch to dark mode");
            themeToggle.setAttribute("title", dark ? "Light mode" : "Dark mode");
        }
    };

    applyTheme(savedTheme || (systemPrefersDark ? "dark" : "light"));

    if (themeToggle) {
        themeToggle.addEventListener("click", () => {
            const nextTheme = document.body.classList.contains("dark-mode") ? "light" : "dark";
            localStorage.setItem("fetal-health-theme", nextTheme);
            applyTheme(nextTheme);
        });
    }

    const revealNodes = document.querySelectorAll("[data-reveal]");

    if ("IntersectionObserver" in window && revealNodes.length) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("revealed");
                        observer.unobserve(entry.target);
                    }
                });
            },
            {
                threshold: 0.16,
                rootMargin: "0px 0px -40px 0px"
            }
        );

        revealNodes.forEach((node) => observer.observe(node));
    } else {
        revealNodes.forEach((node) => node.classList.add("revealed"));
    }

    const predictionForm = document.getElementById("predictionForm");

    if (predictionForm) {
        predictionForm.addEventListener("submit", (event) => {
            const inputs = predictionForm.querySelectorAll('input[type="number"]');
            let valid = true;

            inputs.forEach((input) => {
                if (!input.value || Number.isNaN(Number(input.value))) {
                    input.classList.add("is-invalid");
                    valid = false;
                } else {
                    input.classList.remove("is-invalid");
                }
            });

            if (!valid) {
                event.preventDefault();
                return;
            }

            const submitButton = predictionForm.querySelector("[data-submit-button]");
            if (submitButton) {
                submitButton.classList.add("loading");
                submitButton.setAttribute("aria-busy", "true");
            }
        });
    }
});
