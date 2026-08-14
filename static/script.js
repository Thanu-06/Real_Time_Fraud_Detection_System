const transactionForm = document.getElementById("transactionForm");
const analyzeButton = document.getElementById("analyzeButton");

const resultContainer = document.getElementById("resultContainer");
const resultIcon = document.querySelector(".result-icon");
const resultTitle = document.getElementById("resultTitle");
const resultMessage = document.getElementById("resultMessage");
const probabilityValue = document.getElementById("probabilityValue");
const transactionId = document.getElementById("transactionId");


// =====================================================
// ANALYZE TRANSACTION
// =====================================================

transactionForm.addEventListener("submit", async function (event) {

    event.preventDefault();

    analyzeButton.disabled = true;
    analyzeButton.textContent = "⏳ Analyzing...";

    try {

        // ---------------------------------------------
        // Collect form data
        // ---------------------------------------------

        const transactionData = {

            amount: parseFloat(
                document.getElementById("amount").value
            ),

            transaction_type:
                document.getElementById("transaction_type").value,

            account_age_days: parseInt(
                document.getElementById("account_age_days").value
            ),

            transactions_last_24h: parseInt(
                document.getElementById("transactions_last_24h").value
            ),

            device_changed: parseInt(
                document.getElementById("device_changed").value
            ),

            international: parseInt(
                document.getElementById("international").value
            ),

            transaction_hour: parseInt(
                document.getElementById("transaction_hour").value
            ),

            previous_fraud_count: parseInt(
                document.getElementById("previous_fraud_count").value
            )
        };


        console.log(
            "Sending transaction:",
            transactionData
        );


        // ---------------------------------------------
        // Send request to Flask
        // ---------------------------------------------

        const response = await fetch("/predict", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(transactionData)

        });


        const data = await response.json();


        console.log(
            "Backend response:",
            data
        );


        // ---------------------------------------------
        // Check response
        // ---------------------------------------------

        if (!response.ok || !data.success) {

            throw new Error(
                data.error || "Prediction failed"
            );
        }


        // =====================================================
        // DISPLAY RESULT
        // =====================================================

        resultContainer.style.display = "block";


        // ---------------------------------------------
        // Fraud probability
        // ---------------------------------------------

        const probability =
            parseFloat(data.fraud_probability);


        probabilityValue.textContent =
            (probability * 100).toFixed(2) + "%";


        // ---------------------------------------------
        // Transaction ID
        // ---------------------------------------------

        transactionId.textContent =
            data.transaction_id || "--";


        // =====================================================
        // PREDICTION
        // =====================================================

        if (
            data.prediction &&
            data.prediction.toLowerCase() === "fraud"
        ) {

            // FRAUD

            resultIcon.textContent = "🚨";

            resultTitle.textContent =
                "Fraudulent Transaction Detected";

            resultMessage.textContent =
                "This transaction has been identified as potentially fraudulent.";

        } else {

            // LEGITIMATE

            resultIcon.textContent = "✅";

            resultTitle.textContent =
                "Transaction Appears Legitimate";

            resultMessage.textContent =
                "This transaction appears to be legitimate.";
        }


        // ---------------------------------------------
        // Refresh transaction history
        // ---------------------------------------------

        await loadTransactions();

        // ---------------------------------------------
        // Refresh statistics
        // ---------------------------------------------

        await loadStatistics();

    }

    catch (error) {

        console.error(
            "Prediction Error:",
            error
        );

        alert(
            "Error analyzing transaction: " +
            error.message
        );

    }

    finally {

        analyzeButton.disabled = false;

        analyzeButton.textContent =
            "🔍 Analyze Transaction";
    }

});


// =====================================================
// LOAD RECENT TRANSACTIONS
// =====================================================

async function loadTransactions() {

    const tableBody =
        document.querySelector(
            "#transactionsTableBody"
        );


    if (!tableBody) {

        console.warn(
            "transactionsTableBody not found"
        );

        return;
    }


    try {

        // Show loading message

        tableBody.innerHTML = `
            <tr>
                <td colspan="6">
                    Loading transactions...
                </td>
            </tr>
        `;


        // ---------------------------------------------
        // Fetch transactions
        // ---------------------------------------------

        const response =
            await fetch(
                "/transactions",
                {
                    method: "GET",
                    cache: "no-cache"
                }
            );


        const data =
            await response.json();


        console.log(
            "Transactions API response:",
            data
        );


        if (!response.ok || !data.success) {

            throw new Error(
                data.error ||
                "Failed to load transactions"
            );
        }


        // ---------------------------------------------
        // Check transactions
        // ---------------------------------------------

        if (
            !data.transactions ||
            data.transactions.length === 0
        ) {

            tableBody.innerHTML = `
                <tr>
                    <td colspan="6">
                        No transactions yet.
                    </td>
                </tr>
            `;

            return;
        }


        // Clear loading message

        tableBody.innerHTML = "";


        // =====================================================
        // DISPLAY EACH TRANSACTION
        // =====================================================

        data.transactions.forEach(
            transaction => {

                const row =
                    document.createElement("tr");


                // ---------------------------------------------
                // Fraud probability
                // ---------------------------------------------

                const probability =
                    (
                        parseFloat(
                            transaction.fraud_probability
                        ) * 100
                    ).toFixed(2);


                // ---------------------------------------------
                // Prediction
                // ---------------------------------------------

                let predictionText;


                if (
                    transaction.prediction &&
                    transaction.prediction
                        .toLowerCase() === "fraud"
                ) {

                    predictionText =
                        "🚨 Fraud";

                } else {

                    predictionText =
                        "✅ Legitimate";
                }


                // ---------------------------------------------
                // Create table row
                // ---------------------------------------------

                row.innerHTML = `

                    <td>
                        ${transaction.transaction_id || "--"}
                    </td>

                    <td>
                        ₹${Number(
                            transaction.amount || 0
                        ).toFixed(2)}
                    </td>

                    <td>
                        ${transaction.transaction_type || "--"}
                    </td>

                    <td>
                        ${probability}%
                    </td>

                    <td>
                        ${predictionText}
                    </td>

                    <td>
                        ${transaction.created_at || "--"}
                    </td>

                `;


                tableBody.appendChild(row);

            }
        );

    }

    catch (error) {

        console.error(
            "Error loading transactions:",
            error
        );


        tableBody.innerHTML = `
            <tr>
                <td colspan="6">
                    ❌ Unable to load transactions
                </td>
            </tr>
        `;
    }
}


// =====================================================
// LOAD DASHBOARD STATISTICS
// =====================================================

async function loadStatistics() {

    try {

        const response =
            await fetch(
                "/stats",
                {
                    method: "GET",
                    cache: "no-cache"
                }
            );


        const data =
            await response.json();


        console.log(
            "Statistics:",
            data
        );


        if (!response.ok || !data.success) {

            throw new Error(
                data.error ||
                "Failed to load statistics"
            );
        }


        // ---------------------------------------------
        // Update statistics if elements exist
        // ---------------------------------------------

        const totalElement =
            document.getElementById("totalTransactions");


        const fraudElement =
            document.getElementById("fraudTransactions");


        const legitimateElement =
            document.getElementById(
                "legitimateTransactions"
            );


        if (totalElement) {

            totalElement.textContent =
                data.total;
        }


        if (fraudElement) {

            fraudElement.textContent =
                data.fraud;
        }


        if (legitimateElement) {

            legitimateElement.textContent =
                data.legitimate;
        }

    }

    catch (error) {

        console.error(
            "Error loading statistics:",
            error
        );
    }
}


// =====================================================
// REFRESH BUTTON
// =====================================================

const refreshButton =
    document.getElementById(
        "refreshButton"
    );


if (refreshButton) {

    refreshButton.addEventListener(
        "click",
        async function () {

            refreshButton.disabled = true;

            refreshButton.textContent =
                "⏳ Refreshing...";


            try {

                await loadTransactions();

                await loadStatistics();

            }

            finally {

                refreshButton.disabled = false;

                refreshButton.textContent =
                    "🔄 Refresh";
            }
        }
    );
}


// =====================================================
// INITIAL LOAD
// =====================================================

document.addEventListener(
    "DOMContentLoaded",
    function () {

        loadTransactions();

        loadStatistics();

    }
);