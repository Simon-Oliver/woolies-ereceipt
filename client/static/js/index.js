window.onload = () => {
    const items_table = document.getElementById('items')
    items_table.addEventListener('click', getItems)
    const modalCloseBtn = document.getElementById('modal-close')
    modalCloseBtn.addEventListener('click', toggleModal)
}

const getItems = async (e) => {
    const id = e.target.closest('tr').id
    const store = e.target.closest('tr').getAttribute('data-store')
    const total = e.target.closest('tr').getAttribute('data-total')
    const date = e.target.closest('tr').getAttribute('data-date')


    const response = await fetch(`/items?id=${id}`);
    const test = await response.json()

    const modelData = document.getElementById('model-data')
    const modalHeader = document.getElementById('modal-header')
    const modalSupHeader = document.getElementById('modal-sub')

    const dateObj = new Date(date);
    const options = {year: 'numeric', month: 'short', day: 'numeric'};
    const dateString = dateObj.toLocaleDateString("en-AU", options)

    modalHeader.innerText = `Receipt from ${dateString}`
    modalSupHeader.innerText = `${store} — $${total}`

    modelData.innerHTML = test.map(e => `<tr><td>${e[2]}</td><td>${e[3]}</td><td>${e[4]}</td><td>${e[5]}</td></tr>`).join(" ")
    toggleModal()
}
window.addEventListener('load', function () {
    // close modals on background click
    document.addEventListener('click', event => {
        console.log(event)
        if (event.target.id == 'modal') {
            toggleModal();
        }
    });
});

const toggleModal = (e) => {
    const modal = document.getElementById('modal')
    const isOpen = modal.hasAttribute('open') && modal.getAttribute('open') != 'false' ? true : false;
    isOpen ? modal.close() : modal.show()
}
