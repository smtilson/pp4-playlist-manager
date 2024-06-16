$(document).ready(function () {
    console.log("page loaded");
    initSwapInputs();
    initialize();
})

const DOMAIN = "http://localhost:8000/";
function initialize() {
    const laterBtns = $('.later-btn');
    for (let btn of laterBtns) {
        btn.addEventListener('click', moveLater);
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

async function moveLater(event) {
    const href = event.target.getAttribute("data-href");
    const queueId = href.split("/")[3];
    const entryId = href.split("/")[4];
    console.log(entryId);
    const  otherPosition = event.target.getAttribute("data-position");
    console.log(otherPosition);
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


async function swapEntries(queueId, entryId, otherPosition) {
    const response = await fetch(DOMAIN + `/queues/swap-js/${queueId}/${entryId}/${otherPosition}`, {
        method: 'GET'
    });
    const data = await response.json();
    const entry1 = data.entry1;
    const entry2 = data.entry2;
    writeEntryData(entry1);
    writeEntryData(entry2);
}

testEntryData = {
    entryId: 1,
    entryTitle: "TEST",
    entryPosition: 1,
    addedBy: "test",
    entryDuration: "test"
}
function writeEntryData(entryData) {
    position = entryData.position;
    positionDiv = $(`#div-position-${position}`);
    positionSpan = positionDiv.children('span')[0];
    positionSpan.innerText = entryData.title + " added by " + entryData.user + "(" + entryData.duration + ")";
    for (let button of positionDiv.find('.position-btn')) {
        let addr = button.dataset.href.split('/');
        addr[addr.length - 1] = entryData.id;
        button.dataset.href = addr.join('/');
    }
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
    console.log("validate triggered")
}