$(document).ready(function () {
    console.log("page loaded");
    addListenersNModifyForms();
});

const DOMAIN = setDomain();

console.log("DOMAIN set to:" + DOMAIN);

/**
 * Adds event listeners and modifies forms based on the presence of specific
 * HTML elements.
 *
 * @return {void} This function does not return a value.
 */
function addListenersNModifyForms() {
    const rawHTML = $('html').html();
    if (rawHTML.includes("swap-input")) {
        setSwapPlaceHolderText();
        addSwapListeners();
        console.log("swap-input class present. Listeners added.");
    }
    if (rawHTML.includes("move-btn")) {
        addMoveListeners();
        console.log("move-btn class present. Listeners added.");
    }
    if (rawHTML.includes("<form")) {
        formStyle();
        console.log("Classes added to form elements.");
    }

}

/**
 * Adds event listeners to the swap buttons and attaches the 'swapEntries'
 * function as the event handler.
 *
 * @return {void} This function does not return a value.
 */
function addSwapListeners() {
    const swapBtns = $('.swap-button');
    for (let btn of swapBtns) {
        btn.addEventListener('click', swapEntries);
    }
}

/**
 * Returns the domain URL based on the current hostname.
 *
 * @return {string} The domain URL.
 */
function setDomain() {
    const hostname = window.location.hostname;
    if (hostname === "localhost") {
        return "http://localhost:8000/";
    } else {
        return "https://pp4-playlist-manager-67004a99f0e2.herokuapp.com/";
    }
}

/**
 * Adds event listeners to the move buttons and attaches the 'moveEntry' 
 * function as the event handler.
 *
 * @return {void} This function does not return a value.
 */
function addMoveListeners() {
    const moveBtns = $('.move-btn');
    for (let btn of moveBtns) {
        btn.addEventListener('click', moveEntry);
    }
}

/**
 * Asynchronous function to move an entry based on the provided event data.
 *
 * @param {Event} event - The event triggering the move operation.
 * @return {void} This function does not return a value.
 */
async function moveEntry(event) {
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

/**
 * Asynchronous function to swap two entries in the queue based on the
 * provided event data.
 *
 * @param {Event} event - The event triggering the swap operation.
 * @return {Promise<void>} This function does not return a value.
 */
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

/**
 * Updates the HTML elements with the data from the given entryData object.
 *
 * @param {Object} entryData - The data object containing information about an
 * entry.
 * @param {number} entryData.position - The position of the entry in the queue.
 * @param {string} entryData.title - The title of the entry.
 * @param {string} entryData.user - The user who added the entry.
 * @param {string} entryData.id - The ID of the entry.
 * @return {void} This function does not return a value.
 */
function writeEntryData(entryData) {
    position = entryData.position;
    positionDiv = $(`#div-${position}`);
    positionSpan = positionDiv.find('.entry-display')[0];
    positionSpan.innerText = entryData.position + ". " + entryData.title + " added by " + entryData.user;
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

/**
 * A function to get the queue length.
 *
 * @return {number} The parsed integer value of the queue length.
 */
function getQueueLength() {
    const queueLength = $('#queueLength').text();
    return parseInt(queueLength);
}

/**
 * Sets the placeholder text of all elements with the class 'swap-input' to a
 * range from 1 to the current queue length.
 *
 * @return {void} This function does not return a value.
 */
function setSwapPlaceHolderText() {
    const queueLength = getQueueLength();
    const placeholderText = `1-${queueLength}`;
    swapInputs = $('.swap-input');
    for (let input of swapInputs) {
        console.log("Setting placeholder text.");
        input.setAttribute('placeholder', placeholderText);
    }
}

/**
 * Applies styling to form inputs and labels.
 *
 * @return {void} This function does not return a value.
 */
function formStyle() {
    const inputs = $('input');
    const labels = $('label');
    for (let label of labels) {
        label.classList.add("form-label");
    }
    for (let input of inputs) {
        input.classList.add("js-input-background");
        if (input.id !== "id_remember") {
            input.classList.add("form-control");
        } else {
            input.classList.add("form-check-input");
        }
    }
}

