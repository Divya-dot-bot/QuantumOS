const navigationItems = document.querySelectorAll(".nav-item");

navigationItems.forEach((item) => {
    item.addEventListener("click", () => {

        navigationItems.forEach((nav) => {
            nav.classList.remove("active");
        });

        item.classList.add("active");
    });
});


console.log("QuantumOS Interface initialized.");
console.log("Quantum Core: READY");
console.log("Scheduler: ACTIVE");
console.log("Memory Manager: ACTIVE");