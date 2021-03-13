function createToastHTML(message, colorClass, id, itemTypeId, globalError) {

    return `<div class="toast d-flex align-items-center ${colorClass} text-white ${globalError ? 'globalError' : ''}" id="toast${id}-${itemTypeId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close ms-auto me-2" data-bs-dismiss="toast"
                        aria-label="Close"></button>
            </div>`
}

document.addEventListener("DOMContentLoaded", function (event) {

    const DATA = JSON.parse(document.getElementById('alert-data').textContent);
    const LIBRARY_DATA = JSON.parse(document.getElementById('library-data').textContent);

    Array.from(document.getElementsByClassName('HoldButton')).forEach(function (el) {
        let url = `/placehold/THING/${el.dataset.itemId}/${el.dataset.subitemId}/`;
        if (el.dataset.isItem) {
            url = url.replace("THING", "item")
        } else {
            url = url.replace("THING", "record")
        }


        el.onclick = function () {
            if (document.getElementById(`toast${el.dataset.itemId}-${el.dataset.subitemId}`)) {
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
                let message = DATA['hold_success_message']
                DATA['name_keys']['item_title']
                message = message.replace(DATA['name_keys']['item_title'], el.dataset.title)
                message = message.replace(DATA['name_keys']['item_type_name'], resp['name'])
                message = message.replace(DATA['name_keys']['hold_number'], resp['hold_number'])
                newtoast = createToastHTML(
                    message, colorClass = "bg-success", id = el.dataset.itemId, itemTypeId = el.dataset.subitemId
                )
            }).catch(function (err) {
                if (err.status === 409) {
                    newtoast = createToastHTML(
                        DATA['hold_duplicate'],
                        colorClass = "bg-secondary",
                        id = el.dataset.itemId,
                        itemTypeId = el.dataset.subitemId
                    )
                } else if (err.status === 401) {
                    newtoast = createToastHTML(
                        DATA['not_logged_in'],
                        colorClass = "bg-danger",
                        id = el.dataset.itemId,
                        itemTypeId = el.dataset.subitemId,
                        globalError = true,
                    )
                } else if (parseInt(err.status.toString()[0]) === 5) {
                    newtoast = createToastHTML(
                        `Something went wrong -- please contact ${LIBRARY_DATA['LIBRARY_SYSTEM_NAME']} IT support.`,
                        colorClass = "bg-danger",
                        id = el.dataset.itemId,
                        itemTypeId = el.dataset.subitemId,
                        globalError = true,
                    )
                    console.log(err)
                } else {
                    newtoast = createToastHTML(
                        DATA['hold_error_message'],
                        colorClass = "bg-danger",
                        id = el.dataset.itemId,
                        itemTypeId = el.dataset.subitemId
                    )
                }

            }).finally(function () {
                document.getElementById("toaster").insertAdjacentHTML('beforeend', newtoast);

                let toastEl = document.getElementById(`toast${el.dataset.itemId}-${el.dataset.subitemId}`);
                let toast = new bootstrap.Toast(toastEl, {'delay': 8000});
                toast.show();

                toastEl.addEventListener('hidden.bs.toast', function (event) {
                    toastEl.remove();
                });
            })
        }
    });
});
