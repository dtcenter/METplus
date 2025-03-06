document.addEventListener("DOMContentLoaded", function() {
    var sidebar = document.querySelector(".wy-menu-vertical");
    if (sidebar) {
        sidebar.style.maxHeight = "100vh";
        sidebar.style.overflowY = "auto";
    }
});
