document.addEventListener('DOMContentLoaded', function() {
    // Emoji mapping
    const emojiMap = {
        ':slightly_smiling_face:': '😊',
        ':blush:': '😊',
        ':joy:': '😂',
        ':laughing:': '😂',
        ':heart:': '❤️',
        ':red_heart:': '❤️',
        ':thumbs_up:': '👍',
        ':+1:': '👍',
        ':sweat_smile:': '😅'
    };

    // Function to render emojis in text
    function renderEmojis(text) {
        let renderedText = text;
        for (const [shortcode, emoji] of Object.entries(emojiMap)) {
            const regex = new RegExp(escapeRegExp(shortcode), 'g');
            renderedText = renderedText.replace(regex, emoji);
        }
        return renderedText;
    }

    // Escape special regex characters
    function escapeRegExp(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    // Render emojis in existing messages
    const messageTexts = document.querySelectorAll('.message-text');
    messageTexts.forEach(element => {
        element.innerHTML = renderEmojis(element.textContent);
    });

    // Render emojis in conversation titles and subtitles
    const conversationTitles = document.querySelectorAll('.conversation-info h4, .conversation-info p');
    conversationTitles.forEach(element => {
        element.innerHTML = renderEmojis(element.textContent);
    });
});