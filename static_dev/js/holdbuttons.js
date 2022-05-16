function updateHoldContext(el) {
    window.holdContext = {
        'itemId': el.dataset.itemId,
        'subitemId': el.dataset.subitemId,
        'title': el.dataset.title,
        'subtitle': el.dataset.subtitle,
        'isItem': el.dataset.isItem
    }
}

function cancelHold(el) {
    const DATA = JSON.parse(document.getElementById('alert-data').textContent);
    const LIBRARY_DATA = JSON.parse(document.getElementById('library-data').textContent);

    const url = `/api/holds/${el.dataset.holdId}/`;

    if (toastGlobalErrorExists()) {
        return
    }

    const toastId = `toast${el.dataset.holdId}-0`;

    let newtoast;
    fetch(url, {method: 'DELETE'}).then(function (response) {
        return response.ok ? response : Promise.reject(response);
    }).then(function () {
        // The response was successful, so reload the page to refresh the info.
        // If folks are going to be cancelling a ton of holds at once, then there
        // should be a better way to do this, but for now this is clean and will
        // work nicely.
        window.location.reload();
    }).catch(function (err) {
        if (err.status === 401) {
            newtoast = createToastHTML(DATA['not_logged_in'], colorClass = "bg-danger", id = el.dataset.holdId, itemTypeId = 0, globalError = true,)
        } else if (err.status === 403) {
            newtoast = createToastHTML(DATA['hold_insufficient_permissions'], colorClass = "bg-danger", id = el.dataset.holdId, itemTypeId = 0, globalError = true,)
        } else if (parseInt(err.status.toString()[0]) === 5) {
            console.log('hi');
            newtoast = createToastHTML(`Something went wrong -- please contact ${LIBRARY_DATA['name']} IT support.`, colorClass = "bg-danger", id = el.dataset.holdId, itemTypeId = 0, globalError = true,)
            console.log(err)
        } else {
            newtoast = createToastHTML(DATA['general_error_message'], colorClass = "bg-danger", id = el.dataset.holdId, itemTypeId = 0,)
        }
    }).finally(function () {
        document.getElementById("toaster").insertAdjacentHTML('beforeend', newtoast);

        let toastEl = document.getElementById(toastId);
        let toast = new bootstrap.Toast(toastEl, {'delay': 8000});
        toast.show();

        toastEl.addEventListener('hidden.bs.toast', function (event) {
            toastEl.remove();
        });
    })
}

function processHold() {
    const DATA = JSON.parse(document.getElementById('alert-data').textContent);
    const LIBRARY_DATA = JSON.parse(document.getElementById('library-data').textContent);

    let url = `/api/THING/${window.holdContext['itemId']}/place_hold/`;
    if (window.holdContext['isItem']) {
        url = url.replace("THING", "items")
    } else {
        url = url.replace("THING", "records")
    }

    let locationId = document.getElementById('branchDropdownWithDefaultOnTop').value;
    let postData = {"item_type_id": parseInt(window.holdContext['subitemId']), "location_id": parseInt(locationId)}

    const toastId = `toast${window.holdContext['itemId']}-${window.holdContext['subitemId']}`;

    if (toastAlreadyExists(toastId)) {
        // The toast is already on screen and active, so don't fire the request again
        return
    }

    if (toastGlobalErrorExists()) {
        // There is already a toast on screen showing the error, so don't add another toast
        // with the same error.
        return
    }
    // because this is declared outside the fetch request, it's available inside
    // all the different sections which would normally be closed off from each other.
    let newtoast;
    fetch(url, {
        method: "POST",
        headers: {
            'Accept': 'application/json, text/plain',
            'Content-Type': 'application/json;charset=UTF-8'
        },
        body: JSON.stringify(postData)
    }).then(function (response) {
        return response.ok ? response.json() : Promise.reject(response);
    }).then(function (resp) {
        let message = DATA['hold_success_message'];
        message = message.replace("(itemTitle)", window.holdContext['title']);
        message = message.replace("(itemType)", resp['name']);
        message = message.replace("(holdNum)", resp['hold_number']);
        newtoast = createToastHTML(message, colorClass = "bg-success", id = window.holdContext['itemId'], itemTypeId = window.holdContext['subitemId']);
    }).catch(function (err) {
        if (err.status === 409) {
            newtoast = createToastHTML(DATA['hold_duplicate'], colorClass = "bg-secondary", id = window.holdContext['itemId'], itemTypeId = window.holdContext['subitemId'])
        } else if (err.status === 401) {
            newtoast = createToastHTML(DATA['not_logged_in'], colorClass = "bg-danger", id = window.holdContext['itemId'], itemTypeId = window.holdContext['subitemId'], globalError = true,)
        } else if (err.status === 406) {
            newtoast = createToastHTML(DATA['already_checked_out'], colorClass = "bg-danger", id = window.holdContext['itemId'], itemTypeId = window.holdContext['subitemId'], globalError = true,)
        } else if (parseInt(err.status.toString()[0]) === 5) {
            newtoast = createToastHTML(`Something went wrong -- please contact ${LIBRARY_DATA['name']} IT support.`, colorClass = "bg-danger", id = window.holdContext['itemId'], itemTypeId = window.holdContext['subitemId'], globalError = true,)
            console.log(err)
        } else {
            newtoast = createToastHTML(DATA['general_error_message'], colorClass = "bg-danger", id = window.holdContext['itemId'], itemTypeId = window.holdContext['subitemId'])
        }
    }).finally(function () {
        document.getElementById("toaster").insertAdjacentHTML('beforeend', newtoast);

        let toastEl = document.getElementById(toastId);
        let toast = new bootstrap.Toast(toastEl, {'delay': 8000});
        toast.show();

        toastEl.addEventListener('hidden.bs.toast', function (event) {
            toastEl.remove();
        });
    })
}

function holdbuttonmain() {
    Array.from(document.getElementsByClassName('holdButtonInitial')).forEach(function (el) {
        el.onclick = function () {
            updateHoldContext(el);
        }
    })
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', holdbuttonmain);
} else {
    holdbuttonmain();
}
