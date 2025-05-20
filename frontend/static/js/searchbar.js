document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('search-input');
    const resultsContainer = document.getElementById('search-results');

    input.addEventListener('input', function () {
        const query = input.value.trim();
        if (query.length === 0) {
            resultsContainer.classList.add('hidden');
            resultsContainer.innerHTML = '';
            return;
        }

        fetch(`/search-users/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                const users = data.results;
                if (users.length > 0) {
                    resultsContainer.innerHTML = users.map(user => `
                        <a href="/profile/${encodeURIComponent(user.username)}" class="block py-1 border-b hover:bg-gray-100">
                            <span class="font-semibold">${user.username}</span>
                            <span class="text-sm text-gray-500">(${user.email})</span>
                        </a>
                    `).join('');
                    resultsContainer.classList.remove('hidden');
                } else {
                    resultsContainer.innerHTML = '<div class="text-gray-600">No users found.</div>';
                    resultsContainer.classList.remove('hidden');
                }
            });
    });
});
