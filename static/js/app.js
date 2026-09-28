(function () {
    const balance = document.getElementById("live-balance");
    const cardBalance = document.getElementById("account-card-balance");
    const notifications = document.getElementById("live-notifications");

    if (!balance && !cardBalance && !notifications) return;

    async function refreshLiveData() {
        try {
            const response = await fetch("/api/live-data/", {
                method: "GET",
                headers: {"X-Requested-With": "XMLHttpRequest"},
                cache: "no-store"
            });

            if (!response.ok) return;

            const data = await response.json();

            if (balance) {
                balance.textContent = "₹" + Number(data.balance).toLocaleString("en-IN", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }

            if (cardBalance) {
                cardBalance.textContent = "₹" + Number(data.balance).toLocaleString("en-IN", {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                });
            }

            if (notifications) {
                notifications.textContent = data.unread_notifications;
            }
        } catch (error) {
            // Keep the last displayed value if the server is temporarily unavailable.
        }
    }

    refreshLiveData();
    setInterval(refreshLiveData, 5000);
})();
