document.querySelectorAll('.toggle-password').forEach(function(toggle) {
    toggle.addEventListener('click', function () {
        const targetId = this.getAttribute('data-target');
        const passwordField = document.getElementById(targetId);
        const type = passwordField.type === 'password' ? 'text' : 'password';
        passwordField.type = type;

        // Change the icon
        const icon = this.querySelector('i');
        icon.classList.toggle('fa-eye');
        icon.classList.toggle('fa-eye-slash');
    });
});