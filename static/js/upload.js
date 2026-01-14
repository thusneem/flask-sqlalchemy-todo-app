
const select = document.getElementById("category");
const hidden = document.getElementById("selectedCategory");

select.addEventListener("change", () => {
    hidden.value = select.value;
    console.log("Category set to:", hidden.value);
});

document.getElementById("uploadForm").addEventListener("submit", function () {
    console.log("Submitting category:", hidden.value);
});

