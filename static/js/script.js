document.addEventListener("DOMContentLoaded", function () {

    /* ---------- Mobile sidebar toggle ---------- */
    const toggleBtn = document.getElementById("sidebarToggle");
    const sidebar = document.getElementById("sidebar");

    if (toggleBtn && sidebar) {
        toggleBtn.addEventListener("click", function () {
            sidebar.classList.toggle("show");
        });

        document.addEventListener("click", function (e) {
            if (
                sidebar.classList.contains("show") &&
                !sidebar.contains(e.target) &&
                !toggleBtn.contains(e.target)
            ) {
                sidebar.classList.remove("show");
            }
        });
    }

    /* ---------- Animated stat counters ---------- */
    const counters = document.querySelectorAll(".counter");

    counters.forEach(function (counter) {
        const target = parseInt(counter.getAttribute("data-target"), 10) || 0;
        const duration = 900;
        const startTime = performance.now();

        function tick(now) {
            const progress = Math.min((now - startTime) / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            counter.textContent = Math.round(eased * target);
            if (progress < 1) {
                requestAnimationFrame(tick);
            } else {
                counter.textContent = target;
            }
        }

        requestAnimationFrame(tick);
    });

    /* ---------- Auto-dismiss flash alerts ---------- */
    const alerts = document.querySelectorAll(".alert");
    alerts.forEach(function (alert) {
        setTimeout(function () {
            if (window.bootstrap && bootstrap.Alert) {
                const instance = bootstrap.Alert.getOrCreateInstance(alert);
                instance.close();
            } else {
                alert.remove();
            }
        }, 5000);
    });

});
