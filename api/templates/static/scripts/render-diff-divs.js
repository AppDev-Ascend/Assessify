const urlParams = new URLSearchParams(window.location.search);
const creationType = urlParams.get('type');
var sectionCounter = 0;

document.addEventListener("DOMContentLoaded", function() {
    // A duct-tape solution to a bug, not elegant, but it works.
    addNewSection();

    var title = document.getElementById('header-title');
    var subtitle = document.getElementById('header-subtitle');
    var sectionButton = document.getElementById('section-add-button');
    var icon = document.getElementById('header-icon');

    // Change some elements to accomodate the assessment type.
    if (creationType === 'exam') {
        title.textContent = 'Create Examination Type Assessment';
        subtitle.textContent = 'Exams are a comprehensive assessment on multiple topics. Recommended for long form assessments.';
        sectionButton.style.display = 'block';
        icon.src = "static/media/exam-icon.png";
    }
});

function addNewSection() {
    var newAssessmentSection = document.createElement('div');
    newAssessmentSection.classList.add('assessment-section');
    sectionCounter++;

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
            <input type="text" class="generic-form-textbox" placeholder="Select an option" onclick="toggleDropdown(this)" name="section-length_${sectionCounter}" readonly>
            <ul class="dropdown-options">
                <li onclick="selectOption(this)">5 Items (Pop Quiz Format)</li>
                <li onclick="selectOption(this)">10 Items (Short Assessment Check)</li>
                <li onclick="selectOption(this)">15 Items (Standard Assessments)</li>
                <li onclick="selectOption(this)">30 Items (Comprehensive Assessment Checks)</li>
            </ul>
        </div>

        <label> Learning Outcomes: </label>
        <div class="learning-outcomes" id="learning-outcomes_${sectionCounter}"></div>
        <button class="generic-button-variant" onclick="addInputElement('learning-outcomes_${sectionCounter}')" type="button"> Add Learning Outcome </button>
    `;

    document.getElementById('assessment-section-container').appendChild(newAssessmentSection);
}

function addInputElement(containerID) {
    console.log(containerID);
    var newInput = document.createElement('input');
    var section_no = containerID.split('_')[1];

    newInput.type = 'text';
    newInput.placeholder = `Learning Outcome ${document.getElementById(containerID).childElementCount + 1}`;
    newInput.name = `learning-outcomes_${section_no}_${document.getElementById(containerID).childElementCount + 1}`;

    newInput.classList.add('generic-form-textbox');
    document.getElementById(containerID).appendChild(newInput);
}