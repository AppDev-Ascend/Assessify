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