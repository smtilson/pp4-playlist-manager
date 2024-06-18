$(document).ready(function () {
    console.log("page loaded");
    initSwapInputs();
    initialize();
    initialize();
})

const DOMAIN = "http://localhost:8000/";
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
async function testFetch() {
    const response = await fetch(DOMAIN + "test")
    const data = await response.json();
    console.log(data);
}

async function moveEntry(event) {
    // how do I give feedback in this set up?
    const queueId = event.target.getAttribute("data-queue");
    const entryId = event.target.getAttribute("data-entry");
    const direction = event.target.getAttribute("data-direction");
    console.log(entryId);
    const otherPosition = event.target.getAttribute("data-position");
    console.log(otherPosition);
    if (otherPosition <= 0 && direction === "+") {
        console.log("out of bounds +");
        return;
    } else if (otherPosition > getQueueLength() && direction == "-") {
        console.log("out of bounds -");
        return;
    }
    const response = await fetch(DOMAIN + `/queues/swap-js/${queueId}/${entryId}/${otherPosition}`, {
        method: 'GET'
    });
    const data = await response.json();
    const entry1 = data.entry1;
    console.log(entry1);
    const entry2 = data.entry2;
    console.log(entry2);
    writeEntryData(entry1);
    writeEntryData(entry2);
}


async function swapEntries(event) {
    console.log("swap triggered");
    const queueId = event.target.getAttribute("data-queue");
    console.log(queueId);
    const entryId = event.target.getAttribute("data-entry");
    console.log(entryId);
    const newPosition = $(`#new-position-${entryId}`).val();
    console.log(newPosition);
    if (newPosition < 1 || newPosition > getQueueLength()) {
        console.log("out of bounds");
        return;
    }
    const response = await fetch(DOMAIN + `/queues/swap-js/${queueId}/${entryId}/${newPosition}`, {
        method: 'GET'
    });
    const data = await response.json();
    const entry1 = data.entry1;
    const entry2 = data.entry2;
    writeEntryData(entry1);
    writeEntryData(entry2);
    async function testFetch() {
        const response = await fetch(DOMAIN + "test")
        const data = await response.json();
        console.log(data);
    }
}

async function moveEntry(event) {
    // how do I give feedback in this set up?
    const queueId = event.target.getAttribute("data-queue");
    const entryId = event.target.getAttribute("data-entry");
    const direction = event.target.getAttribute("data-direction");
    console.log(entryId);
    const otherPosition = event.target.getAttribute("data-position");
    console.log("other position"+otherPosition);
    if (otherPosition <= 0 && direction === "+") {
        console.log("out of bounds +");
        return;
    } else if (otherPosition > getQueueLength() && direction == "-") {
        console.log("out of bounds -");
        return;
    }
    const response = await fetch(DOMAIN + `/queues/swap/${queueId}/${entryId}/${otherPosition}`, {
        method: 'GET'
    });
    const data = await response.json();
    const entry1 = data.entry1;
    console.log(entry1.position);
    const entry2 = data.entry2;
    console.log(entry2.position);
    console.log("going to wriet entry data");
    writeEntryData(entry1);
    writeEntryData(entry2);
}


async function swapEntries(event) {
    console.log("swap triggered");
    const queueId = event.target.getAttribute("data-queue");
    console.log(queueId);
    const entryId = event.target.getAttribute("data-entry");
    console.log(entryId);
    const newPosition = $(`#new-position-${entryId}`).val();
    console.log(newPosition);
    if (newPosition < 1 || newPosition > getQueueLength()) {
        console.log("out of bounds");
        return;
    }
    const response = await fetch(DOMAIN + `/queues/swap-js/${queueId}/${entryId}/${newPosition}`, {
        method: 'GET'
    });
    const data = await response.json();
    const entry1 = data.entry1;
    const entry2 = data.entry2;
    writeEntryData(entry1);
    writeEntryData(entry2);
}

function writeEntryData(entryData) {
    position = entryData.position;
    console.log(entryData.title);
    console.log(position);
    positionDiv = $(`#div-position-${position}`);
    positionSpan = positionDiv.children('span')[0];
    positionSpan.innerText = entryData.title + " added by " + entryData.user + "(" + entryData.duration + ")";
    for (let button of positionDiv.find('.position-btn')) {
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
