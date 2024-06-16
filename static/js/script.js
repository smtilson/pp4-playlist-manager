$(document).ready(function () {
    console.log("page loaded");
    initSwapInputs();
})

const DOMAIN = "http://localhost:8000";
function initialize() {

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

function swapEntries(queueId, entryId, otherPosition) {
    fetch(DOMAIN + `/queues/swap-js/${queueId}/${entryId}/${otherPosition}`, {
        method: 'GET',
    })//.then(response => console.log(response.json))

}

testEntryData = {
    entryId: 1,
    entryTitle: "TEST",
    entryPosition: 1,
    addedBy: "test",
    entryDuration: "test"
}
function writeEntryData(entryData, position) {
    positionDiv = $(`#div-position-${position}`);
    positionSpan = positionDiv.children('span')[0];
    positionSpan.innerText = entryData.entryTitle + " added by " + entryData.addedBy + "(" + entryData.entryDuration + ")";
    for (let anchorTag of positionDiv.find('a')) {
        let addr = anchorTag.href.split('/');
        addr[addr.length - 1] = entryData.entryId;
        anchorTag.href = addr.join('/');
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