document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('checkout-container');
  if (!container) return;

  const csrfToken = document.querySelector('input[name="csrf_token"]').value;
  const removeUrl = container.dataset.removeUrl;
  const checkoutUrl = container.dataset.checkoutUrl;
  const dashboardUrl = container.dataset.dashboardUrl;

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
      body: JSON.stringify({ group_id: gid })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        const li = document.querySelector(`#checkout-list li[data-id="${gid}"]`);
        if (li) li.remove();
        const newCount = data.basket_count;
        document.getElementById('total-count').textContent = newCount;
        document.getElementById('confirm-btn').disabled = newCount === 0;
      } else {
        alert(data.message);
      }
    })
    .catch(err => console.error('Error removing item:', err));
  }

  document.querySelectorAll('.remove-btn').forEach(btn => btn.addEventListener('click', removeHandler));

  document.getElementById('confirm-btn').addEventListener('click', evt => {
    evt.preventDefault();
    fetch(checkoutUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      credentials: 'same-origin'
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        console.log('Checkout response:', data);
        window.location.href = dashboardUrl;
      } else {
        alert(data.message);
      }
    })
    .catch(err => console.error('Error confirming checkout:', err));
  });
});
