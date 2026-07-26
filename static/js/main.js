/* ==========================================================================
   Aura Health - Global JavaScript Manager
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initChatbot();
});

// Theme Toggler
function initTheme() {
    const savedTheme = localStorage.getItem('aura_theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeIcon(savedTheme);

    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    if (themeToggleBtn) {
        themeToggleBtn.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            document.documentElement.setAttribute('data-theme', newTheme);
            localStorage.setItem('aura_theme', newTheme);
            updateThemeIcon(newTheme);
        });
    }
}

function updateThemeIcon(theme) {
    const icon = document.querySelector('#theme-toggle-btn i');
    if (icon) {
        icon.className = theme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
    }
}

// Toast Notifications
function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let iconClass = 'fa-info-circle';
    if (type === 'success') iconClass = 'fa-check-circle';
    if (type === 'danger') iconClass = 'fa-exclamation-circle';
    if (type === 'warning') iconClass = 'fa-exclamation-triangle';

    toast.innerHTML = `<i class="fas ${iconClass}"></i><span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// AI Chatbot Interface
function initChatbot() {
    const toggleBtn = document.getElementById('ai-chatbot-toggle');
    const windowEl = document.getElementById('ai-chat-window');
    const closeBtn = document.getElementById('ai-chat-close');
    const sendBtn = document.getElementById('ai-chat-send');
    const inputEl = document.getElementById('ai-chat-input');
    const bodyEl = document.getElementById('ai-chat-body');

    if (!toggleBtn || !windowEl) return;

    toggleBtn.addEventListener('click', () => {
        windowEl.style.display = windowEl.style.display === 'flex' ? 'none' : 'flex';
    });

    if (closeBtn) {
        closeBtn.addEventListener('click', () => windowEl.style.display = 'none');
    }

    const sendMessage = async () => {
        const text = inputEl.value.trim();
        if (!text) return;

        // Render user message
        const userMsg = document.createElement('div');
        userMsg.className = 'chat-msg user';
        userMsg.textContent = text;
        bodyEl.appendChild(userMsg);

        inputEl.value = '';
        bodyEl.scrollTop = bodyEl.scrollHeight;

        // Bot loading indicator
        const botLoading = document.createElement('div');
        botLoading.className = 'chat-msg bot';
        botLoading.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analyzing...';
        bodyEl.appendChild(botLoading);

        try {
            const res = await fetch('/ai/voice-assistant', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: text })
            });
            const data = await res.json();

            botLoading.remove();
            const botMsg = document.createElement('div');
            botMsg.className = 'chat-msg bot';
            botMsg.textContent = data.response;
            bodyEl.appendChild(botMsg);

            // Optional Voice Synthesis
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(data.response);
                window.speechSynthesis.speak(utterance);
            }

            if (data.action === 'navigate' && data.target) {
                setTimeout(() => window.location.href = data.target, 2000);
            }
        } catch (e) {
            botLoading.textContent = 'Sorry, AI response error. Please try again.';
        }

        bodyEl.scrollTop = bodyEl.scrollHeight;
    };

    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (inputEl) {
        inputEl.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') sendMessage();
        });
    }
}
