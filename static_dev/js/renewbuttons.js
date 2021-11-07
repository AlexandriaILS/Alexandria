function processRenew(el) {
    const DATA = JSON.parse(document.getElementById('alert-data').textContent);
    const LIBRARY_DATA = JSON.parse(document.getElementById('library-data').textContent);
    let url = `/renewhold/${el.dataset.itemId}/`;

    let toastId = `toast${el.dataset.itemId}-${el.dataset.subitemId}`;

    if (toastAlreadyExists(toastId)) {
        // The toast is already on screen and active, so don't fire the request again
        return
    }

    if (toastGlobalErrorExists()) {
        return
    }

    let newtoast;
    fetch(url).then(function (response) {
        return response.ok ? response.json() : Promise.reject(response);
    }).then(function (resp) {
        console.log('success?');
        newtoast = createToastHTML(
            DATA['renew_success_message'],
            colorClass = "bg-success",
            id = el.dataset.itemId,
            itemTypeId = el.dataset.subitemId
        );
        // make it look like what a page refresh would do
        el.classList.remove('btn-primary');
        el.classList.add('btn-secondary');
        el.classList.add('disabled');
        let dueDate = el.parentElement.parentElement.parentElement.parentElement.parentElement.children[2].children[0].children[1].children[1];
        dueDate.classList.remove('bg-warning');
        dueDate.classList.remove('text-dark');
        dueDate.classList.add('text-light');
        dueDate.classList.add('bg-secondary');
        dueDate.textContent = resp['new_due_date'];

    }).catch(function (err) {
        if (parseInt(err.status.toString()[0]) === 5) {
            newtoast = createToastHTML(
                `Something went wrong -- please contact ${LIBRARY_DATA['name']} IT support.`,
                colorClass = "bg-danger",
                id = el.dataset.itemId,
                itemTypeId = el.dataset.subitemId,
                globalError = true,
            );
            console.log(err);
        } else if (err.status === 401) {
            newtoast = createToastHTML(
                DATA['not_logged_in'],
                colorClass = "bg-danger",
                id = el.dataset.itemId,
                itemTypeId = el.dataset.subitemId,
                globalError = true,
            )
        } else {
            newtoast = createToastHTML(
                DATA['general_error_message'],
                colorClass = "bg-danger",
                id = el.dataset.itemId,
                itemTypeId = el.dataset.subitemId
            );
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
