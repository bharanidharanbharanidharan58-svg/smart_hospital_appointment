/* ==========================================================================
   Aura Health - Web Speech API & AI Voice Assistant (English + Tamil)
   ========================================================================== */

class VoiceAssistant {
    constructor() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.lang = 'en-US';
            this.isListening = false;
            this.setupListeners();
        } else {
            console.warn('Web Speech API (SpeechRecognition) is not supported in this browser.');
        }
    }

    setLanguage(langCode) {
        // 'en-US' or 'ta-IN'
        this.lang = langCode;
        if (this.recognition) {
            this.recognition.lang = langCode;
        }
    }

    setupListeners() {
        this.recognition.onstart = () => {
            this.isListening = true;
            this.onListeningStateChange(true);
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.onListeningStateChange(false);
        };

        this.recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.onSpeechResult(transcript);
        };

        this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isListening = false;
            this.onListeningStateChange(false);
        };
    }

    start() {
        if (this.recognition && !this.isListening) {
            this.recognition.lang = this.lang;
            this.recognition.start();
        }
    }

    stop() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    speak(text, lang = 'en-US') {
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel(); // stop previous speech
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = lang;
            utterance.rate = 1.0;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }
    }

    // Callbacks to be overridden
    onListeningStateChange(listening) {}
    onSpeechResult(transcript) {}
}

// Global Voice Assistant Instance
const auraVoice = new VoiceAssistant();

// Voice button handler binding
document.addEventListener('DOMContentLoaded', () => {
    const micBtn = document.getElementById('voice-mic-btn');
    const voiceStatus = document.getElementById('voice-status-text');
    const voiceInput = document.getElementById('ai-symptom-input');
    const langSelect = document.getElementById('voice-lang-select');

    if (micBtn) {
        micBtn.addEventListener('click', () => {
            if (auraVoice.isListening) {
                auraVoice.stop();
            } else {
                const selectedLang = langSelect ? langSelect.value : 'en-US';
                auraVoice.setLanguage(selectedLang);
                auraVoice.start();
            }
        });

        auraVoice.onListeningStateChange = (listening) => {
            if (listening) {
                micBtn.classList.add('pulse-glow', 'btn-danger');
                micBtn.classList.remove('btn-primary');
                if (voiceStatus) voiceStatus.textContent = 'Listening... Speak your symptoms clearly';
            } else {
                micBtn.classList.remove('pulse-glow', 'btn-danger');
                micBtn.classList.add('btn-primary');
                if (voiceStatus) voiceStatus.textContent = 'Click microphone to start voice input';
            }
        };

        auraVoice.onSpeechResult = (transcript) => {
            if (voiceInput) voiceInput.value = transcript;
            showToast(`Voice Recognized: "${transcript}"`, 'info');
            
            // Auto trigger symptom analyzer if on symptom checker page
            const analyzeBtn = document.getElementById('run-symptom-analysis-btn');
            if (analyzeBtn) analyzeBtn.click();
        };
    }
});
