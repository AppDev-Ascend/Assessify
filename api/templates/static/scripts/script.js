var elementCounter = 2;
document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('overlay').addEventListener('click', closePrompt);
});

document.addEventListener("input", function(event) {
    if (event.target && event.target.classList.contains("generic-textarea")) {
    var textarea = event.target;
    textarea.style.height = "auto";
    textarea.style.height = (textarea.scrollHeight) + "px";
    }
});

function rl_showLogin() {
    var register_div = document.getElementById('register-container');
    var login_div = document.getElementById('login-container');

    if (login_div.style.display === 'none') {
        login_div.style.display = 'block';
        register_div.style.display = 'none';
    }
}

function rl_swapContentBox() {
    var register_div = document.getElementById('register-container');
    var login_div = document.getElementById('login-container');

    if (login_div.style.display === 'none') {
        login_div.style.display = 'block';
        register_div.style.display = 'none';
    } else {
        login_div.style.display = 'none';
        register_div.style.display = 'block';
    }
}

function showPrompt() {
    document.getElementById('promptContainer').style.display = 'flex';
    document.getElementById('overlay').style.display = 'block';
}

function closePrompt() {
    document.getElementById('promptContainer').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
}

// Closes the dropdown if the user clicks outside of it
window.onclick = function(event) {
    var dropdownContainers = document.querySelectorAll('.dropdown-container');
    dropdownContainers.forEach(function(container) {
        var dropdownOptions = container.querySelector('.dropdown-options');
        if (dropdownOptions.style.display === 'block' && !event.target.matches('.generic-form-textbox') && !event.target.matches('.dropdown-options li')) {
        dropdownOptions.style.display = 'none';
        }
    });
}

function toggleDropdown(input) {
    var dropdownOptions = input.nextElementSibling;
    dropdownOptions.style.display = (dropdownOptions.style.display === 'block') ? 'none' : 'block';
  }

  // Select an option and populate the input field
function selectOption(option) {
    var inputField = option.parentElement.previousElementSibling;
    inputField.value = option.textContent;
    toggleDropdown(inputField);
}

function displayFileName(input) {
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const fileName = input.files[0] ? input.files[0].name : 'No file chosen';
    fileNameDisplay.textContent = fileName;
}