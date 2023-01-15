window.onload = () => {
    const items_table = document.getElementById('items')
    items_table.addEventListener('click', getItems)
}

const getItems = async (e) => {
    const id = e.target.id
    const response = await fetch(`/items?id=${id}`);
    const test = await response.json()
    console.log(test)
    const modelData = document.getElementById('model-data')
    modelData.innerHTML = test.map(e => `<li>${e[2]}</li>`).join(" ")
    openModal('modal-1')
}


function openModal(id) {
    document.getElementById(id).classList.add('open');
    document.body.classList.add('jw-modal-open');
}

// close currently open modal
function closeModal() {
    document.querySelector('.jw-modal.open').classList.remove('open');
    document.body.classList.remove('jw-modal-open');
}

window.addEventListener('load', function () {
    // close modals on background click
    document.addEventListener('click', event => {
        if (event.target.classList.contains('jw-modal')) {
            closeModal();
        }
    });
});