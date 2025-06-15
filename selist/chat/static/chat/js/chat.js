document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('send-button');
    const messageInput = document.getElementById('message-input');
    const modal = document.getElementById('trade-type-modal');
    const demandBtn = document.getElementById('demand-btn');
    const offerBtn = document.getElementById('offer-btn');
    const cancelBtn = document.getElementById('cancel-btn');
    const emojiBtn = document.getElementById('emoji-btn');
    const emojiPicker = document.getElementById('emoji-picker');
    const chatMessages = document.getElementById('chat-messages');
    
    let currentMessage = '';
    const isInAgora = currentConversation === null && recipientId === null;

    // Scroll to bottom on page load
    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    scrollToBottom();

    // Emoji picker functionality
    if (emojiBtn && emojiPicker) {
        // Toggle emoji picker
        emojiBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            emojiPicker.style.display = emojiPicker.style.display === 'none' ? 'block' : 'none';
        });

        // Handle emoji selection
        const emojiItems = document.querySelectorAll('.emoji-item');
        emojiItems.forEach(item => {
            item.addEventListener('click', function() {
                const shortcode = this.getAttribute('data-shortcode');
                const currentPos = messageInput.selectionStart;
                const currentValue = messageInput.value;
                
                messageInput.value = currentValue.slice(0, currentPos) + shortcode + currentValue.slice(currentPos);
                
                messageInput.selectionStart = messageInput.selectionEnd = currentPos + shortcode.length;
                messageInput.focus();
                
                emojiPicker.style.display = 'none';
            });
        });

        document.addEventListener('click', function(e) {
            if (!emojiPicker.contains(e.target) && e.target !== emojiBtn) {
                emojiPicker.style.display = 'none';
            }
        });
    }

    // Handle send button click
    sendButton.addEventListener('click', function() {
        const message = messageInput.value.trim();
        if (message) {
            currentMessage = message;
            
            if (isInAgora) {
                // In Agora: show modal to create trade
                modal.style.display = 'flex';
            } else {
                // In Trade conversation: send text message directly
                sendTextMessage(message);
            }
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

    // Handle trade type selection (only for Agora)
    demandBtn.addEventListener('click', function() {
        createTrade('demand');
    });

    offerBtn.addEventListener('click', function() {
        createTrade('offer');
    });

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
            demandBtn.disabled = false;
            offerBtn.disabled = false;
            cancelBtn.disabled = false;
            
            closeModal();
            messageInput.value = '';
        });
    }

    function sendTextMessage(message) {
        sendButton.disabled = true;
        messageInput.disabled = true;

        // Prepare the request body based on conversation type
        let requestBody = {
            message: message
        };

        if (currentConversation) {
            // Existing conversation (trade or private)
            requestBody.conversation_type = currentConversation.type;
            requestBody.conversation_id = currentConversation.id;
        } else if (recipientId) {
            // New private conversation
            requestBody.conversation_type = 'private';
            requestBody.recipient_id = recipientId;
        }

        fetch(sendMessageUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // If this was a new private conversation, redirect to the conversation
                if (data.conversation_id && !currentConversation) {
                    window.location.href = `/chat/conversation/${data.conversation_id}/`;
                } else {
                    // Reload page to show new message
                    location.reload();
                }
            } else {
                alert('Erreur: ' + (data.error || 'Une erreur est survenue'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erreur de connexion');
        })
        .finally(() => {
            // Re-enable inputs
            sendButton.disabled = false;
            messageInput.disabled = false;
        });
    }
});