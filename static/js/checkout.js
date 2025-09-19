document.getElementById('confirm-btn').addEventListener('click', evt => {
  evt.preventDefault();

  // Step 1: Confirm Checkout
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
    if (!data.success) {
      alert(data.message);
      return;
    }

    // Step 2: Send Email
    fetch('/send_group_links', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
      },
      credentials: 'same-origin',
      body: JSON.stringify({ csrf_token: csrfToken })
    })
    .then(res => res.json())
    .then(emailData => {
      if (emailData.success) {
        alert("✅ Checkout complete! Group links sent to your email.");
        window.location.href = dashboardUrl;
      } else {
        alert("⚠️ Checkout complete, but email failed: " + emailData.message);
      }
    })
    .catch(err => {
      console.error("Error sending email:", err);
      alert("⚠️ Checkout complete, but failed to send email.");
      window.location.href = dashboardUrl;
    });

  })
  .catch(err => {
    console.error('Checkout error:', err);
    alert("❌ Checkout failed. Please try again.");
  });
});
