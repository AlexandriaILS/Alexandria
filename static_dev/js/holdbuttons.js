function createToastHTML(message, colorClass, id, itemTypeId, globalError) {
    return `<div class="toast d-flex align-items-center ${colorClass} text-white ${globalError ? 'globalError' : ''}" id="toast${id}-${itemTypeId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close ms-auto me-2" data-bs-dismiss="toast"
                        aria-label="Close"></button>
            </div>`
}

function updateHoldContext(el) {
    window.holdContext = {
        'itemId': el.dataset.itemId,
        'subitemId': el.dataset.subitemId,
        'title': el.dataset.title,
        'subtitle': el.dataset.subtitle,
        'isItem': el.dataset.isItem
    }
}

function processHold() {
    const DATA = JSON.parse(document.getElementById('alert-data').textContent);
    const LIBRARY_DATA = JSON.parse(document.getElementById('library-data').textContent);

    let locationId = document.getElementById('holdBranchSelector').value;
    let url = `/placehold/THING/${window.holdContext['itemId']}/${window.holdContext['subitemId']}/${locationId}/`;
    if (window.holdContext['isItem']) {
        console.log("ITEM!")
        url = url.replace("THING", "item")
    } else {
        console.log("RECORD!")
        url = url.replace("THING", "record")
    }


    if (document.getElementById(`toast${window.holdContext['itemId']}-${window.holdContext['subitemId']}`)) {
        // The toast is already on screen and active, so don't fire the request again
        return
    }

    if (document.getElementsByClassName("globalError").length > 0) {
        // There is already a toast on screen showing the error, so don't add another toast
        // with the same error.
        return
    }
    // because this is declared outside the fetch request, it's available inside
    // all the different sections which would normally be closed off from each other.
    let newtoast;
    fetch(url).then(function (response) {
        return response.ok ? response.json() : Promise.reject(response);
    }).then(function (resp) {
        let message = DATA['hold_success_message'];
        message = message.replace("(itemTitle)", window.holdContext['title']);
        message = message.replace("(itemType)", resp['name']);
        message = message.replace("(holdNum)", resp['hold_number']);
        newtoast = createToastHTML(
            message, colorClass = "bg-success", id = window.holdContext['itemId'], itemTypeId = window.holdContext['subitemId']
        );
    }).catch(function (err) {
        if (err.status === 409) {
            newtoast = createToastHTML(
                DATA['hold_duplicate'],
                colorClass = "bg-secondary",
                id = window.holdContext['itemId'],
                itemTypeId = window.holdContext['subitemId']
            )
        } else if (err.status === 401) {
            newtoast = createToastHTML(
                DATA['not_logged_in'],
                colorClass = "bg-danger",
                id = window.holdContext['itemId'],
                itemTypeId = window.holdContext['subitemId'],
                globalError = true,
            )
        } else if (parseInt(err.status.toString()[0]) === 5) {
            newtoast = createToastHTML(
                `Something went wrong -- please contact ${LIBRARY_DATA['name']} IT support.`,
                colorClass = "bg-danger",
                id = window.holdContext['itemId'],
                itemTypeId = window.holdContext['subitemId'],
                globalError = true,
            )
            console.log(err)
        } else {
            newtoast = createToastHTML(
                DATA['hold_error_message'],
                colorClass = "bg-danger",
                id = window.holdContext['itemId'],
                itemTypeId = window.holdContext['subitemId']
            )
        }
    }).finally(function () {
        document.getElementById("toaster").insertAdjacentHTML('beforeend', newtoast);

        let toastEl = document.getElementById(`toast${window.holdContext['itemId']}-${window.holdContext['subitemId']}`);
        let toast = new bootstrap.Toast(toastEl, {'delay': 8000});
        toast.show();

        toastEl.addEventListener('hidden.bs.toast', function (event) {
            toastEl.remove();
        });
    })
}

function main() {
    Array.from(document.getElementsByClassName('holdButtonInitial')).forEach(function (el) {
        el.onclick = function () {
            updateHoldContext(el);
        }
    })
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
} else {
    main();
}
