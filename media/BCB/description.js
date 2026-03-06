const description = document.getElementById('description');
const toggleBtn = document.getElementById('showMoreBtn');

toggleBtn.addEventListener('click', function () {
    if (description.classList.contains('expanded')) {
        description.classList.remove('expanded');
        toggleBtn.textContent = 'SHOW MORE';
    } else {
        description.classList.add('expanded');
        toggleBtn.textContent = 'SHOW LESS';
    }
});