document.querySelectorAll('.js-delete-form').forEach(function (form) {
    form.addEventListener('submit', function (event) {
        var ok = confirm('Удалить эту привычку? Действие нельзя отменить.');
        if (!ok) {
            event.preventDefault();
        }
    });
});
