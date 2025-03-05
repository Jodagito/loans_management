function confirmAction(event) {
    if (confirm("Are you sure you want to perform this action?")) {
        return true
    }
    event.preventDefault();
}

function performAction(event, element) {
    event.preventDefault();
    if (confirmAction()) {
        window.location.href = element.href;
    }
}