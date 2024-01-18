document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("assessment-creation-form").addEventListener("submit", function (event) {
        var textboxes = document.querySelectorAll(".generic-form-textbox");
        var textarea = document.getElementById("material-textarea");
        var fileUploaded = document.getElementById("material-file-upload");

        // Flag to track if all textboxes are filled
        var allFilled = true;
        var materialsProvided = false;

        // I'm about to have an aneurysm on fileUploaded.value's undefined behavior so I'm skipping it.
        textboxes.forEach(function (textbox) {
            if (textbox.value.trim() === "") { allFilled = false; }
        });
        if (textarea.value.trim() !== "") { materialsProvided = true; }

        if (allFilled === false || materialsProvided === false) {
            displayErrorPopup();
        }
    });
});

function displayErrorPopup() {
    document.getElementById('promptContainer').style.display = 'flex';
    document.getElementById('overlay').style.display = 'block';
}