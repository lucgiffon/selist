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

    // Transaction functionality
    const validateTradeBtn = document.getElementById('validate-trade-btn');
    const transactionModal = document.getElementById('transaction-modal');
    const transactionAmount = document.getElementById('transaction-amount');
    const transactionRecipient = document.getElementById('transaction-recipient');
    const recipientGroup = document.getElementById('recipient-group');
    const fixedRecipientGroup = document.getElementById('fixed-recipient-group');
    const fixedRecipientName = document.getElementById('fixed-recipient-name');
    const confirmTransactionBtn = document.getElementById('confirm-transaction-btn');
    const cancelTransactionBtn = document.getElementById('cancel-transaction-btn');
    const confirmBtnText = document.getElementById('confirm-btn-text');
    const transactionModalTitle = document.getElementById('transaction-modal-title');
    const transactionTargetLabel = document.getElementById('transaction-target-label');
    const transactionFixedTargetLabel = document.getElementById('transaction-fixed-target-label');
    const transactionAmountLabel = document.getElementById('transaction-amount-label');

    let currentTransactionMode = null; // 'direct' or 'proposal'
    let currentRecipientId = null;

    if (validateTradeBtn && currentConversation && currentConversation.type === 'trade') {
        validateTradeBtn.addEventListener('click', function() {
            openTransactionModal();
        });
    }

    if (cancelTransactionBtn) {
        cancelTransactionBtn.addEventListener('click', function() {
            closeTransactionModal();
        });
    }

    if (transactionModal) {
        transactionModal.addEventListener('click', function(e) {
            if (e.target === transactionModal) {
                closeTransactionModal();
            }
        });
    }

    if (confirmTransactionBtn) {
        confirmTransactionBtn.addEventListener('click', function() {
            handleTransactionConfirm();
        });
    }

    // Handle proposal accept/refuse buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.accept-btn')) {
            const btn = e.target.closest('.accept-btn');
            const proposalId = btn.getAttribute('data-proposal-id');
            acceptProposal(proposalId);
        } else if (e.target.closest('.refuse-btn')) {
            const btn = e.target.closest('.refuse-btn');
            const proposalId = btn.getAttribute('data-proposal-id');
            refuseProposal(proposalId);
        }
    });

    function openTransactionModal() {
        if (!currentConversation || currentConversation.type !== 'trade') return;

        // Fetch trade participants
        fetch(`/chat/trade/${currentConversation.trade_id}/participants/`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    populateTransactionModal(data);
                    transactionModal.style.display = 'flex';
                } else {
                    alert('Erreur: ' + (data.error || 'Une erreur est survenue'));
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Erreur de connexion');
            });
    }

    function populateTransactionModal(data) {
        const { participants, trade_type, trade_initiator } = data;
        
        const isInitiator = currentUserId === trade_initiator;
        
        if (trade_type === 'demand') {
            if (isInitiator) {
                transactionModalTitle.textContent = 'Finaliser l\'échange';
                transactionAmountLabel.textContent = 'Montant à transférer';
                transactionTargetLabel.textContent = 'Destinataire';
                transactionRecipient.innerHTML = '<option value="">Choisir un destinataire</option>';
                transactionTargetLabel.textContent = 'Destinataire';
                currentTransactionMode = 'direct';
                confirmBtnText.textContent = 'Transférer';
                recipientGroup.style.display = 'block';
                fixedRecipientGroup.style.display = 'none';
            } else {
                transactionModalTitle.textContent = 'Proposer un échange';
                transactionAmountLabel.textContent = 'Montant à recevoir';
                transactionFixedTargetLabel.textContent = 'Expéditeur';
                transactionRecipient.innerHTML = '<option value="">Expéditeur</option>';
                currentTransactionMode = 'proposal';
                confirmBtnText.textContent = 'Proposer';
                recipientGroup.style.display = 'none';
                fixedRecipientGroup.style.display = 'block';
                fixedRecipientName.textContent = getInitiatorName(participants, trade_initiator);
                currentRecipientId = trade_initiator;
            }
        } else { // offer
            if (isInitiator) {
                transactionModalTitle.textContent = 'Proposer un échange';
                transactionAmountLabel.textContent = 'Montant à recevoir';
                transactionTargetLabel.textContent = 'Expéditeur';
                transactionRecipient.innerHTML = '<option value="">Choisir un expéditeur</option>';
                currentTransactionMode = 'proposal';
                confirmBtnText.textContent = 'Proposer';
                recipientGroup.style.display = 'block';
                fixedRecipientGroup.style.display = 'none';
            } else {
                transactionModalTitle.textContent = 'Finaliser l\'échange';
                transactionAmountLabel.textContent = 'Montant à transférer';
                transactionFixedTargetLabel.textContent = 'Destinataire';
                transactionRecipient.innerHTML = '<option value="">Destinataire</option>';
                currentTransactionMode = 'direct';
                confirmBtnText.textContent = 'Transférer';
                recipientGroup.style.display = 'none';
                fixedRecipientGroup.style.display = 'block';
                fixedRecipientName.textContent = getInitiatorName(participants, trade_initiator);
                currentRecipientId = trade_initiator;
            }
        }

        // Populate recipients dropdown
        if (recipientGroup.style.display !== 'none') {
            participants.forEach(participant => {
                const option = document.createElement('option');
                option.value = participant.id;
                option.textContent = participant.username;
                transactionRecipient.appendChild(option);
            });
        }
    }


    function getInitiatorName(participants, initiatorId) {
        const allUsers = [...participants];
        for (let participant of allUsers) {
            if (participant.id === initiatorId) {
                return participant.username;
            }
        }
        return 'Initiateur';
    }

    function handleTransactionConfirm() {
        const amount = parseInt(transactionAmount.value);
        const recipientId = currentTransactionMode === 'direct' ? 
            (currentRecipientId || parseInt(transactionRecipient.value)) :
            (currentRecipientId || parseInt(transactionRecipient.value));

        if (!amount || amount <= 0) {
            alert('Veuillez entrer un montant valide');
            return;
        }

        if (!recipientId) {
            alert('Veuillez choisir un destinataire');
            return;
        }

        const tradeId = currentConversation.trade_id;

        if (currentTransactionMode === 'direct') {
            directTransfer(tradeId, amount, recipientId);
        } else {
            createProposal(tradeId, amount, recipientId);
        }
    }

    function directTransfer(tradeId, amount, recipientId) {
        confirmTransactionBtn.disabled = true;

        fetch('/chat/direct-transfer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                trade_id: tradeId,
                amount: amount,
                recipient_id: recipientId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeTransactionModal();
                location.reload(); // Refresh to show new message
            } else {
                alert('Erreur: ' + (data.error || 'Une erreur est survenue'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erreur de connexion');
        })
        .finally(() => {
            confirmTransactionBtn.disabled = false;
        });
    }

    function createProposal(tradeId, amount, recipientId) {
        confirmTransactionBtn.disabled = true;

        fetch('/chat/create-proposal/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                trade_id: tradeId,
                amount: amount,
                other_user_id: recipientId
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                closeTransactionModal();
                location.reload(); // Refresh to show new message
            } else {
                alert('Erreur: ' + (data.error || 'Une erreur est survenue'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erreur de connexion');
        })
        .finally(() => {
            confirmTransactionBtn.disabled = false;
        });
    }

    function acceptProposal(proposalId) {
        if (!confirm('Accepter cette proposition ?')) return;

        fetch('/chat/answer-proposal/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                proposal_id: proposalId,
                accepted: true
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Refresh to show updated status
            } else {
                alert('Erreur: ' + (data.error || 'Une erreur est survenue'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erreur de connexion');
        });
    }

    function refuseProposal(proposalId) {
        if (!confirm('Refuser cette proposition ?')) return;

        fetch('/chat/answer-proposal/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                proposal_id: proposalId,
                accepted: false
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload(); // Refresh to show updated status
            } else {
                alert('Erreur: ' + (data.error || 'Une erreur est survenue'));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Erreur de connexion');
        });
    }

    function closeTransactionModal() {
        transactionModal.style.display = 'none';
        transactionAmount.value = '';
        transactionRecipient.selectedIndex = 0;
        currentTransactionMode = null;
        currentRecipientId = null;
    }
});