$(document).ready(function () {
    console.log("page loaded");
    initSwapInputs();
    initialize();
    formStyle();
})

const sampleDomain = window.location.hostname;
console.log("The current sample domain is " + sampleDomain);
const DOMAIN = "http://localhost:8000/";
//const DOMAIN = "https://pp4-playlist-manager-67004a99f0e2.herokuapp.com/";
console.log("The current domain is " + DOMAIN);
function initialize() {
    const moveBtns = $('.move-btn');
    for (let btn of moveBtns) {
        btn.addEventListener('click', moveEntry);
    }
    const swapBtns = $('.swap-button');
    console.log("adding listeners to swap buttons");
    for (let btn of swapBtns) {
        btn.addEventListener('click', swapEntries);
    }
}

function getQueueLength() {
    const length = $('#queueLength').text();
    return length;
}

function initSwapInputs() {
    console.log("initializing swap inputs");
    const queueLength = getQueueLength();
    setSwapPlaceHolderText(queueLength);
}

async function moveEntry(event) {
    // how do I give feedback in this set up?
    const entryId = event.target.getAttribute("data-entry");
    const direction = event.target.getAttribute("data-direction");
    const otherPosition = event.target.getAttribute("data-position");
    if (otherPosition <= 0 && direction === "+") {
        console.log("out of bounds +");
        return;
    } else if (otherPosition > getQueueLength() && direction == "-") {
        console.log("out of bounds -");
        return;
    }
    //const address = DOMAIN + `queues/swap/${entryId}/${otherPosition}`;
    //console.log(address);
    const response = await fetch(DOMAIN + `queues/swap/${entryId}/${otherPosition}`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        },
    });
    const data = await response.json();
    const entry1 = data.entry1;
    const entry2 = data.entry2;
    console.log("going to write entry data");
    writeEntryData(entry1);
    console.log("entry 1 written");
    writeEntryData(entry2);
    console.log("entry 2 written");
}

async function swapEntries(event) {
    console.log("swap triggered");
    const entryId = event.target.getAttribute("data-entry");
    console.log(entryId);
    const newPosition = $(`#new-position-${entryId}`).val();
    console.log(newPosition);
    if (newPosition < 1 || newPosition > getQueueLength()) {
        console.log("out of bounds");
        return;
    }
    const response = await fetch(DOMAIN + `queues/swap/${entryId}/${newPosition}`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
            'Content-Type': 'application/json',
        },
    });
    const data = await response.json();
    const entry1 = data.entry1;
    const entry2 = data.entry2;
    writeEntryData(entry1);
    writeEntryData(entry2);
}

function writeEntryData(entryData) {
    position = entryData.position;
    positionDiv = $(`#div-${position}`);
    positionSpan = positionDiv.find('h4')[0];
    positionSpan.innerText = entryData.position + ". " + entryData.title + " added by " + entryData.user + "(" + entryData.duration + ")";
    for (let button of positionDiv.find('.move-btn')) {
        button.setAttribute("data-entry", entryData.id);
        if (button.getAttribute("data-direction") == "+") {
            button.setAttribute("data-position", position - 1);
        }
        else if (button.getAttribute("data-direction") == "-") {
            button.setAttribute("data-position", position + 1);
        }
    }
    let input = positionDiv.find('input')[0];
    let label = positionDiv.find("label")[0];
    input.setAttribute("id", `new-position-${entryData.id}`);
    label.setAttribute("for", `new-position-${entryData.id}`);
    label.setAttribute("id", `label-${entryData.id}`);
}

function setSwapPlaceHolderText(queueLength) {
    const placeholderText = `1-${queueLength}`;
    swapInputs = $('.swap-input');
    for (let input of swapInputs) {
        console.log("setting value");
        input.setAttribute('placeholder', placeholderText);
    }
}

function addSwapListeners() {
    swapInputs = $('.swap-input');
    for (let input of swapInputs) {
        input.addEventListener('input', validateSwapInputs);
    }
}

function initSwapForms() {
    forms = $(".swapForm");
    for (let form of forms) {
        form.addEventListener('submit', validateSwapInputs);
    }
}

function validateSwapInputs(entryId) {
    // get input for that particular entry
    // check if input is valid
    // if not valid, display error
    // if valid, display button
    console.log("validate triggered");
}

function formStyle() {
    const inputs = $('input');
    const labels = $('label');
    for (let label of labels) {
        label.classList.add("form-label");
    }
    for (let input of inputs) {
        input.classList.add("js-input-background");
        input.classList.add("form-control");
    }
    console.log("form style done");
}