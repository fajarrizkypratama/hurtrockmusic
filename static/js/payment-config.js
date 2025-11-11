document.addEventListener("DOMContentLoaded", function () {
  const providerCards = document.querySelectorAll(".provider-card");
  const selectedProviderInput = document.getElementById("selectedProvider");
  const configFormCard = document.getElementById("configFormCard");
  const providerName = document.getElementById("providerName");
  const submitBtn = document.getElementById("submitBtn");
  const sandboxToggle = document.getElementById("sandboxToggle");
  const environmentLabel = document.getElementById("environmentLabel");
  const environmentDescription = document.getElementById(
    "environmentDescription"
  );
  const providerAlert = document.getElementById("providerAlert");

  const providerForms = {
    midtrans: document.getElementById("midtransForm"),
    stripe: document.getElementById("stripeForm"),
    xendit: document.getElementById("xenditForm"),
    doku: document.getElementById("dokuForm"),
  };

  providerCards.forEach((card) => {
    card.addEventListener("click", function () {
      const provider = this.getAttribute("data-provider");

      providerCards.forEach((c) => c.classList.remove("selected"));
      this.classList.add("selected");

      selectedProviderInput.value = provider;

      Object.values(providerForms).forEach((form) => {
        if (form) form.style.display = "none";
      });

      if (providerForms[provider]) {
        providerForms[provider].style.display = "block";
      }

      providerName.textContent =
        provider.charAt(0).toUpperCase() + provider.slice(1);

      configFormCard.style.display = "block";

      submitBtn.disabled = false;

      providerAlert.style.display = "none";

      configFormCard.scrollIntoView({ behavior: "smooth", block: "nearest" });
    });
  });

  sandboxToggle.addEventListener("change", function () {
    if (this.checked) {
      environmentLabel.textContent = "Sandbox Mode";
      environmentDescription.textContent =
        "Gunakan untuk testing dan development";
    } else {
      environmentLabel.textContent = "Production Mode";
      environmentDescription.textContent =
        "Gunakan untuk transaksi live/production";
    }
  });

  document
    .getElementById("paymentConfigForm")
    .addEventListener("submit", function (e) {
      if (!selectedProviderInput.value) {
        e.preventDefault();
        providerAlert.style.display = "block";
        providerAlert.scrollIntoView({ behavior: "smooth", block: "center" });
        return false;
      }
    });
  // Get current domain for callback URLs
  const currentDomain = window.location.origin;

  // Update callback URL displays
  function updateCallbackUrls() {
    const elements = {
      finishUrl: currentDomain + "/payment/finish",
      unfinishUrl: currentDomain + "/payment/unfinish",
      errorUrl: currentDomain + "/payment/error",
      notificationUrl: currentDomain + "/notification/handling",
      recurringUrl: currentDomain + "/notification/recurring",
      accountLinkingUrl: currentDomain + "/notification/account-linking",
      stripeWebhookUrl: currentDomain + "/payment/notification",
      xenditWebhookUrl: currentDomain + "/webhook/xendit",
      dokuWebhookUrl: currentDomain + "/webhook/doku",
    };

    Object.keys(elements).forEach((id) => {
      const element = document.getElementById(id);
      if (element) {
        element.textContent = elements[id];
      }
    });
  }

  // Initialize callback URLs
  updateCallbackUrls();
});
