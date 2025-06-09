document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('send-button');
    const messageInput = document.getElementById('message-input');
    const modal = document.getElementById('trade-type-modal');
    const demandBtn = document.getElementById('demand-btn');
    const offerBtn = document.getElementById('offer-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    
    let currentMessage = '';

    // Handle send button click
    sendButton.addEventListener('click', function() {
        // if no message is input, clicking "send" doesn't trigger the popup
        const message = messageInput.value.trim();
        if (message) {
            currentMessage = message;
            modal.style.display = 'flex';
        }
    });

    // Handle Enter key in textarea
    messageInput.addEventListener('keypress', function(e) {
        // shift + enter is allowed in text so that multi line text is possible
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendButton.click();
        }
    });

    // Handle trade type selection
    demandBtn.addEventListener('click', function() {
        createTrade('demand');
    });

    offerBtn.addEventListener('click', function() {
        createTrade('offer');
    });

    // Handle cancel button
    cancelBtn.addEventListener('click', function() {
        closeModal();
    });

    // Handle click outside modal
    modal.addEventListener('click', function(e) {
        // this works because the modal span the whole screen
        if (e.target === modal) {
            closeModal();
        }
    });

    // Handle escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'flex') {
            closeModal();
        }
    });

    function closeModal() {
        modal.style.display = 'none';
        currentMessage = '';
    }

    function createTrade(type) {
        // Disable buttons during request
        demandBtn.disabled = true;
        offerBtn.disabled = true;
        cancelBtn.disabled = true;

        fetch(createTradeUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: currentMessage,
                type: type
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reload page to show new message
                location.reload();
            } else {
                alert('Erreur: ' + (data.error || 'Une erreur est survenue'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erreur de connexion');
        })
        .finally(() => {
            // Re-enable buttons
            demandBtn.disabled = false;
            offerBtn.disabled = false;
            cancelBtn.disabled = false;
            
            closeModal();
            messageInput.value = '';
        });
    }
});