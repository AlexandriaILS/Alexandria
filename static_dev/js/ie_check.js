// https://stackoverflow.com/a/22551342
var ua = window.navigator.userAgent;
var isIE = /MSIE|Trident/.test(ua);

if (isIE) {
    document.addEventListener("DOMContentLoaded", function (event) {
        const ie_alert = document.createElement("div");
        ie_alert.className = "alert alert-danger shadow";
        ie_alert.role = "alert";
        // ie doesn't support template literals, so stitching together text
        // is what we get
        ie_alert.innerHTML = (
            "It looks like you're using Internet Explorer."
            + " Many features of this website will not function as expected."
            + ' <a href="https://www.google.com/chrome/"'
            + ' target="_blank"'
            + ' class="alert-link"'
            + ">Please upgrade to a modern browser.</a>");
        const main_el = document.getElementById("theContent");
        main_el.insertBefore(ie_alert, main_el.firstChild);
    })
}
