let productData = []

window.onload = async () => {
    const items_table = document.getElementById('items')
    items_table.addEventListener('click', getItems)

    // const modalCloseBtn = document.getElementById('modal-close')
    // modalCloseBtn.addEventListener('click', toggleModal)

    const refreshBtn = document.getElementById('refreshBtn')
    refreshBtn.addEventListener('click', btnRefresh)

    const searchInput = document.getElementById('product-name')
    searchInput.addEventListener('input', onSearchChange)

    productData = await getProducts()
    renderProducts(productData)
}


const onSearchChange = (e) => {
    console.log(e.target.value)
    const search = e.target.value.toLowerCase()
    let newArr = productData
    if (search.length > 0) {
        newArr = productData.filter(item => item[0].toLowerCase().includes(search))
    }
    renderProducts(newArr)
}

const renderProducts = (products) => {
    const productsItem = document.getElementById('products')
    productsItem.innerHTML = products.map(e => `<tr><td>${e[0]}</td><td>${e[1].toFixed(2)}</td><td>${e[2]}</td><td>$${e[3].toFixed(2)}</td></tr>`).join(" ")
}

const getProducts = async () => {
    const response = await fetch('/products')
    const data = await response.json()
    return data
}

const getItems = async (e) => {
    const id = e.target.closest('tr').id
    const store = e.target.closest('tr').getAttribute('data-store')
    const total = e.target.closest('tr').getAttribute('data-total')
    const date = e.target.closest('tr').getAttribute('data-date')


    const response = await fetch(`/items?id=${id}`);
    const data = await response.json()

    const modelData = document.getElementById('model-data')
    const modalHeader = document.getElementById('modal-header')
    const modalSupHeader = document.getElementById('modal-sub')

    const dateObj = new Date(date);
    const options = {year: 'numeric', month: 'short', day: 'numeric'};
    const dateString = dateObj.toLocaleDateString("en-AU", options)

    modalHeader.innerText = `Receipt from ${dateString}`
    modalSupHeader.innerText = `${store} — $${total}`

    modelData.innerHTML = data.map(e => `<tr><td>${e[2]}</td><td>${e[3]}</td><td>${e[4]}</td><td>${e[5]}</td></tr>`).join(" ")
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

const btnRefresh = async () =>{
    const progressBar = document.getElementById('progress-bar')
    progressBar.show()
    // document.getElementById('indeterminate-progress').indeterminate = true;
    console.log("Button has been triggered")
    const response = await fetch(`/refresh`);
    const data = await response.json()
    console.log(data)
    progressBar.close()
    location.reload()
}
