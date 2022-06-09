function launchModal(src, title) {
    const image = document.getElementById('modal-image');
    image.setAttribute('src', src);
    image.setAttribute('title', title);
    const modal = document.getElementById('modal');
    const currentClass = modal.getAttribute('class');
    modal.setAttribute('class', currentClass + ' show');
}

function closeModal() {
    const modal = document.getElementById('modal');
    modal.className = 'tc-modal';
}

window.onload = function () {
    const images = document.getElementsByTagName("img");
    for (let i = 0; i < images.length; i++) {
        images[i].addEventListener("click", function () {
            launchModal(this.src, this.title);
        });
    }
    document.getElementById("modal").addEventListener("click", closeModal)
};
