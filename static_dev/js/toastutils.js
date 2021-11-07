function createToastHTML(message, colorClass, id, itemTypeId, globalError) {
    console.log('creating toast');
    return `<div class="toast d-flex align-items-center ${colorClass} text-white ${globalError ? 'globalError' : ''}" id="toast${id}-${itemTypeId}" role="alert" aria-live="assertive" aria-atomic="true">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close ms-auto me-2" data-bs-dismiss="toast"
                        aria-label="Close"></button>
            </div>`
}

function toastAlreadyExists(toastId) {
    return document.getElementById(toastId)
}

function toastGlobalErrorExists() {
    return document.getElementsByClassName("globalError").length > 0
}
