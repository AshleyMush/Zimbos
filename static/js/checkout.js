document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('checkout-container');
  if (!container) return;

  const csrfToken = document.querySelector('#csrf-form input[name="csrf_token"]').value;
  const removeUrl = container.dataset.removeUrl;
  const checkoutUrl = container.dataset.checkoutUrl;
  const dashboardUrl = container.dataset.dashboardUrl;

  // Handle removal of a group item during checkout
  function removeHandler(event) {
    const btn = event.currentTarget;
    const gid = btn.getAttribute('data-id');

    fetch(removeUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      credentials: 'same-origin',
      body: JSON.stringify({ group_id: gid, csrf_token: csrfToken })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        // Remove the <li> from the DOM
        const li = document.querySelector(`#checkout-list li[data-id=\"${gid}\"]`);
        if (li) li.remove();

        // Update the total count and button state
        const totalCountEl = document.getElementById('total-count');
        totalCountEl.textContent = data.basket_count;
        document.getElementById('confirm-btn').disabled = data.basket_count === 0;
      } else {
        alert(data.message);
      }
    })
    .catch(err => console.error('Error removing item:', err));
  }

  // Attach removeHandler to all remove buttons
  document.querySelectorAll('.remove-btn').forEach(btn => btn.addEventListener('click', removeHandler));

  // Confirm checkout remains unchanged
  document.getElementById('confirm-btn').addEventListener('click', evt => {
    evt.preventDefault();
    fetch(checkoutUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      credentials: 'same-origin',
      body: JSON.stringify({ csrf_token: csrfToken })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        window.location.href = dashboardUrl;
      } else {
        alert(data.message);
      }
    })
    .catch(err => console.error('Error confirming checkout:', err));
  });
});
