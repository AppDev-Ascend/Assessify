document.addEventListener("DOMContentLoaded", function() {
    let slideIndex = 0;
    showSlides();

    function showSlides() {
        let slides = document.getElementsByClassName("slideshow-image");

        // Check if there are slides and if slideIndex is within valid range
        if (slides.length > 0) {
            // Hide all slides
            for (let i = 0; i < slides.length; i++) {
            slides[i].style.display = "none";
            }

            // Increment slideIndex and check if it's within range
            slideIndex++;
            if (slideIndex > slides.length) {
            slideIndex = 1;
            }

            // Display the current slide
            slides[slideIndex - 1].style.display = "block";

            // Set the timeout for the next slide
            setTimeout(showSlides, 7500);
        } else {
            console.error("No slides found with class 'slideshow-image'");
        }
    }
});

// Append the other files
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
    var login_nav = document.getElementById('nav-element-login')
    var register_nav = document.getElementById('nav-element-register')

    if (login_div.style.display === 'none') {
        login_div.style.display = 'block';
        register_div.style.display = 'none';

    } else {
        login_div.style.display = 'none';
        register_div.style.display = 'block';
    }

    if(login_nav.style.display === 'none') {
        login_nav.style.display = 'flex';
        register_nav.style.display = 'none';
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
    console.log("Display file name called")
    const fileNameDisplay = document.getElementById('fileNameDisplay');
    const fileName = input.files[0] ? input.files[0].name : 'No file chosen';
    fileNameDisplay.textContent = fileName;
    document.getElementById('removeFile').style.display = 'block'; // Show the remove file button
}
  
function removeTheFile() {
    console.log("Remove file called")
    document.getElementById('fileInput').value = '';
    document.getElementById('fileNameDisplay').textContent = 'No file chosen';
    document.getElementById('removeFile').style.display = 'none'; // Hide the remove file button
}

window.onload = function() {
    var input = document.getElementById('fileInput');
    var fileName = input.files[0] ? input.files[0].name : 'No file chosen';
    
    if (fileName !== 'No file chosen') {
        document.getElementById('removeFile').style.display = 'block'; // Show the remove file button
    } 
    
    document.getElementById('fileNameDisplay').textContent = fileName;
}

const urlParams = new URLSearchParams(window.location.search);
const creationType = urlParams.get('type');
var sectionCounter = 1;

document.addEventListener("DOMContentLoaded", function() {
    // A duct-tape solution to a bug, not elegant, but it works.
    addNewSection();

    var title = document.getElementById('header-title');
    var subtitle = document.getElementById('header-subtitle');
    var sectionButton = document.getElementById('section-add-button');
    var icon = document.getElementById('header-icon');

    // Change some elements to accomodate the assessment type.
    if (creationType === 'exam') {
        title.textContent = 'Create Exam Type Assessment';
        subtitle.textContent = 'Exams are a comprehensive assessment on multiple topics. Recommended for long form assessments.';
        sectionButton.style.display = 'block';
        icon.src = "../media/exam-icon.png";
    }
});

function addNewSection() {

    if(creationType == "exam") {
        var newAssessmentSection = document.createElement('div');
        newAssessmentSection.classList.add('assessment-section');

        newAssessmentSection.innerHTML = `
            <h2 class="exam-part"> Section ${sectionCounter} </h2> <br>
            <label> Assessment Type </label>
            <div class="dropdown-container">
                <input type="text" class="generic-form-textbox" placeholder="Select an option" onclick="toggleDropdown(this)" name="section-type_${sectionCounter}" readonly>
                <ul class="dropdown-options">
                <li onclick="selectOption(this)">Multiple Choice</li>
                <li onclick="selectOption(this)">True or False</li>
                <li onclick="selectOption(this)">Fill in The Blanks</li>
                <li onclick="selectOption(this)">Identification</li>
                <li onclick="selectOption(this)">Essay</li>
                </ul>
            </div>
            
            <label> Assessment Length </label>
            <div class="dropdown-container">
                <input type="number" class="generic-form-textbox" name="section-length_${sectionCounter}" min="1" max="20">
            </div>

            <label> Learning Outcomes: </label>
            <div class="learning-outcomes" id="learning-outcomes_${sectionCounter}"></div>
            <button class="generic-button-variant" onclick="addInputElement('learning-outcomes_${sectionCounter}')" type="button"> Add Learning Outcome </button>
        `;

        document.getElementById('assessment-section-container').appendChild(newAssessmentSection);
        sectionCounter++;
    }
    
}

var learningOutcomeCounter = 0;
function addInputElement(containerID) {
    learningOutcomeCounter++;
    var newContainer = document.createElement('div');
    var newInput = document.createElement('input');
    var deleteButton = document.createElement('button');

    newInput.type = 'text';
    newInput.placeholder = `Learning Outcome ${learningOutcomeCounter}`;
    newInput.name = `learning-outcomes_${learningOutcomeCounter}`;

    deleteButton.textContent = 'X';
    deleteButton.onclick = function() {
        newContainer.remove();
        learningOutcomeCounter--;
    };

    newInput.classList.add('generic-form-textbox');
    deleteButton.classList.add('learning-outcome-delete-button');
    newContainer.classList.add('learning-outcome-container');
    
    newContainer.appendChild(newInput);
    newContainer.appendChild(deleteButton);

    document.getElementById(containerID).appendChild(newContainer);
}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById("assessment-creation-form").addEventListener("submit", function (event) {
        var textboxes = document.querySelectorAll(".generic-form-textbox");
        var textarea = document.getElementById("material-textarea");
        var fileUploaded = document.getElementById("fileInput");

        // Flag to track if all textboxes are filled
        var allFilled = true;
        var materialsProvided = false;

        // I'm about to have an aneurysm on fileUploaded.value's undefined behavior so I'm skipping it.
        textboxes.forEach(function (textbox) {
            if (textbox.value.trim() === "") { allFilled = false; }
        });
        
        if (textarea.value.trim() === "" ) { 
            console.log("textarea is empty")
            if (fileUploaded.value !== "") {
                materialsProvided = true; 
            }
        }

        if (fileUploaded.value === "") {
            console.log("fileUpload is empty")
            if (textarea.value.trim() !== "") {
                materialsProvided = true;
            } 
        }

        if (allFilled === true) { 
            console.log("allFilled is True") 
        } else { 
            console.log("allFilled is False") 
        }

        if (materialsProvided === true) { 
            console.log("materialsProvided is True") 
        } else { 
            console.log("materialsProvided is False") 
        } 

        if (allFilled === false || materialsProvided === false) {
            console.log("something is False");
            document.getElementById('promptContainer').style.display = 'flex';
            document.getElementById('overlay').style.display = 'block';
            event.preventDefault()
        } else {
            console.log("all are true");
        }
        
    });
});