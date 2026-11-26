// Small presentation-only helpers. All database operations remain in the Flask routes.
document.addEventListener('DOMContentLoaded', function () {
    document.querySelectorAll('[data-dismiss-message]').forEach(function (button) {
        button.addEventListener('click', function () {
            button.closest('.flash-message')?.remove();
        });
    });

    // Print only the receipt. Browser print styling handles page layout.
    document.querySelectorAll('[data-print-order]').forEach(function (button) {
        button.addEventListener('click', function () { window.print(); });
    });

    const orderForm = document.getElementById('new-order-form');
    if (!orderForm) return;

    const quantities = Array.from(orderForm.querySelectorAll('input.qty'));
    const countLabel = document.getElementById('order-count');
    const totalLabel = document.getElementById('order-total');

    function updateOrderPreview() {
        let count = 0;
        let total = 0;
        quantities.forEach(function (input) {
            if (input.disabled) return;
            const quantity = Math.max(0, Math.floor(Number(input.value) || 0));
            const price = Number(input.dataset.price) || 0;
            count += quantity;
            total += quantity * price;
            input.closest('.order-item')?.classList.toggle('has-quantity', quantity > 0);
        });
        if (countLabel) countLabel.textContent = count.toString();
        if (totalLabel) totalLabel.textContent = '₱' + total.toFixed(2);
    }

    // Quantity steppers are purely visual conveniences. The original qty_*
    // input names and POST form submission are left untouched.
    orderForm.querySelectorAll('[data-step]').forEach(function (button) {
        button.addEventListener('click', function () {
            const input = button.closest('.quantity-stepper')?.querySelector('input.qty');
            if (!input || input.disabled) return;
            const current = Math.max(0, Math.floor(Number(input.value) || 0));
            const step = Number(button.dataset.step) || 0;
            input.value = String(Math.max(0, current + step));
            input.dispatchEvent(new Event('input', { bubbles: true }));
        });
    });

    quantities.forEach(function (input) {
        input.addEventListener('input', updateOrderPreview);
        input.addEventListener('change', updateOrderPreview);
    });
    updateOrderPreview();
});
