
const categorySelect = document.querySelector('select[name="category"]');
const hiddenCategory = document.getElementById("selectedCategory");

if (categorySelect && hiddenCategory) {
    categorySelect.addEventListener("change", function () {
        hiddenCategory.value = this.value;
        console.log("Hidden category set to:", hiddenCategory.value);
    });
}
