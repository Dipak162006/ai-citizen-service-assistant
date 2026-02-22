document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const profileDisplay = document.getElementById('profile-display');

    let sessionId = localStorage.getItem('chat_session_id');

    // Sidebar State Management
    const appWrapper = document.getElementById('app-wrapper');
    const isMobile = window.innerWidth <= 768;
    
    // --- User Preferences & Settings ---
    let userPreferences = {
        theme: 'dark', // 'dark' | 'light'
        textSize: 'medium', // 'small' | 'medium' | 'large'
        autoTts: false,
        highContrast: false
    };

    // Load from LocalStorage immediately
    const loadPreferences = () => {
        const saved = localStorage.getItem('app_preferences_' + (window.userId || 'guest'));
        if (saved) {
            try { userPreferences = { ...userPreferences, ...JSON.parse(saved) }; } 
            catch(e) { console.error("Pref Parse Error:", e); }
        }
    };

    const applyPreferences = () => {
        // Theme
        if (userPreferences.theme === 'light') {
            document.body.classList.add('theme-light');
            localStorage.setItem('site_theme', 'light');
        } else {
            document.body.classList.remove('theme-light');
            localStorage.setItem('site_theme', 'dark');
        }

        // Text Size
        document.body.classList.remove('text-size-small', 'text-size-large');
        if (userPreferences.textSize === 'small') document.body.classList.add('text-size-small');
        if (userPreferences.textSize === 'large') document.body.classList.add('text-size-large');

        // High Contrast
        if (userPreferences.highContrast) document.body.classList.add('high-contrast');
        else document.body.classList.remove('high-contrast');

        // Update UI forms to match state (if modal is open)
        const themeDarkOpt = document.getElementById('theme-dark');
        const themeLightOpt = document.getElementById('theme-light');
        if(themeDarkOpt && userPreferences.theme === 'dark') themeDarkOpt.checked = true;
        if(themeLightOpt && userPreferences.theme === 'light') themeLightOpt.checked = true;

        const textSizeOpt = document.getElementById('setting-textsize');
        if(textSizeOpt) textSizeOpt.value = userPreferences.textSize;

        const autoTtsOpt = document.getElementById('setting-autotts');
        if(autoTtsOpt) autoTtsOpt.checked = userPreferences.autoTts;

        const highContrastOpt = document.getElementById('setting-highcontrast');
        if(highContrastOpt) highContrastOpt.checked = userPreferences.highContrast;
    };

    window.updatePreference = (key, value) => {
        userPreferences[key] = value;
        localStorage.setItem('app_preferences_' + (window.userId || 'guest'), JSON.stringify(userPreferences));
        applyPreferences();
    };

    window.openSettingsModal = () => {
        const modal = new bootstrap.Modal(document.getElementById('settingsModal'));
        modal.show();
    };

    // Initialize Preferences
    loadPreferences();
    applyPreferences();
    // ------------------------------------

    // Load saved state or default to collapsed on mobile
    const savedSidebarState = localStorage.getItem('sidebarState');
    if (savedSidebarState === 'collapsed' || (isMobile && !savedSidebarState)) {
        appWrapper.classList.add('sidebar-collapsed');
    }

    // Global toggle function
    window.toggleSidebar = () => {
        appWrapper.classList.toggle('sidebar-collapsed');
        const isCollapsed = appWrapper.classList.contains('sidebar-collapsed');
        localStorage.setItem('sidebarState', isCollapsed ? 'collapsed' : 'open');
    };

    // Global close function for mobile overlay
    window.closeSidebarMobile = () => {
        if (window.innerWidth <= 768) {
            appWrapper.classList.add('sidebar-collapsed');
            localStorage.setItem('sidebarState', 'collapsed');
        }
    };

    // --- Session History Logic ---
    window.loadSessions = async () => {
        const historyBox = document.getElementById('session-history-box');
        if (!historyBox) return;

        try {
            const res = await fetch('/api/sessions');
            const data = await res.json();
            
            if (data.sessions && data.sessions.length > 0) {
                const sessionsHtml = data.sessions.map(s => `
                    <div class="session-item d-flex align-items-center justify-content-between p-2 rounded mb-1 ${sessionId === s.id ? 'active' : ''}" 
                         onclick="loadSessionContent('${s.id}')" style="cursor: pointer;">
                        <div class="d-flex align-items-center gap-2 overflow-hidden">
                            <i class="fas fa-comment-dots theme-text-secondary" style="font-size: 0.85rem;"></i>
                            <span class="text-truncate small theme-text-primary" style="max-width: 150px;">${s.title}</span>
                        </div>
                        <button class="btn btn-link btn-sm p-0 text-danger opacity-50 hover-opacity-100 delete-session-btn" 
                                onclick="event.stopPropagation(); deleteSession('${s.id}')">
                            <i class="fas fa-trash-alt" style="font-size: 0.7rem;"></i>
                        </button>
                    </div>
                `).join('');
                historyBox.innerHTML = sessionsHtml;
            } else {
                historyBox.innerHTML = '<div class="text-secondary small fst-italic py-2 text-center opacity-50">No recent history...</div>';
            }
        } catch (e) {
            console.error("Failed to load sessions:", e);
        }
    };

    window.loadSessionContent = async (id) => {
        if (id === sessionId) return;

        // Show loading state in chat
        chatBox.innerHTML = '<div class="text-center py-5 opacity-50"><i class="fas fa-spinner fa-spin fa-2x mb-3"></i><p>Loading conversation...</p></div>';
        
        try {
            const res = await fetch(`/api/sessions/${id}`);
            const data = await res.json();
            
            if (data.messages) {
                sessionId = data.session_id;
                localStorage.setItem('chat_session_id', sessionId);
                
                // Clear and Render
                chatBox.innerHTML = '';
                data.messages.forEach(msg => {
                    if (msg.role === 'user') renderUserMessage(msg.content);
                    else renderAssistantMessage(msg.content);
                });
                
                // Load profile context
                if (data.profile) {
                    updateProfileGlobals(data.profile);
                    fetchRecommendations();
                }

                // Refresh history UI highlight
                loadSessions();
                
                // UX: Ensure History section is expanded
                const historyCollapse = document.getElementById('collapseHistory');
                if (historyCollapse && !historyCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(historyCollapse, { toggle: false });
                    bsCollapse.show();
                }

                scrollToBottom();
            }
        } catch (e) {
            console.error("Failed to load session content:", e);
            chatBox.innerHTML = '<div class="text-danger text-center py-5">Failed to load conversation.</div>';
        }
    };

    window.deleteSession = async (id) => {
        if (!confirm("Are you sure you want to delete this conversation?")) return;
        
        try {
            const res = await fetch(`/api/sessions/${id}`, { method: 'DELETE' });
            if (res.ok) {
                if (id === sessionId) {
                    startNewChat();
                } else {
                    loadSessions();
                }
            }
        } catch (e) {
            console.error("Delete failed:", e);
        }
    };

    window.startNewChat = async () => {
        try {
            const res = await fetch('/api/sessions/new', { method: 'POST' });
            const data = await res.json();
            if (data.session_id) {
                sessionId = data.session_id;
                localStorage.setItem('chat_session_id', sessionId);
                
                // Reset UI
                chatBox.innerHTML = '<div class="text-secondary small fst-italic mt-2 text-center opacity-50">New session started...</div>';
                if(profileDisplay) profileDisplay.textContent = 'None yet';
                
                // Reset Profile State
                window.userProfile = {
                    occupation: '',
                    income_range: '',
                    state: '',
                    age: ''
                };
                
                loadSessions();
                
                // UX: Ensure History section is expanded
                const historyCollapse = document.getElementById('collapseHistory');
                if (historyCollapse && !historyCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(historyCollapse, { toggle: false });
                    bsCollapse.show();
                }

                fetchRecommendations();
            }
        } catch (e) {
            console.error("Failed to start new chat:", e);
        }
    };


    // Scroll to bottom
    const scrollToBottom = () => {
        chatBox.scrollTop = chatBox.scrollHeight;
    };

    // Helper to get icon
    const getCategoryIcon = (category) => {
        const cat = category.toLowerCase();
        if (cat.includes('farm') || cat.includes('agri')) return 'fa-tractor';
        if (cat.includes('student') || cat.includes('edu')) return 'fa-user-graduate';
        if (cat.includes('health') || cat.includes('med')) return 'fa-heartbeat';
        if (cat.includes('woman') || cat.includes('female')) return 'fa-venus';
        if (cat.includes('senior') || cat.includes('pen')) return 'fa-blind';
        if (cat.includes('business') || cat.includes('loan')) return 'fa-briefcase';
        return 'fa-hand-holding-heart';
    };

    // --- Translation Manager & Caching ---
    const TranslationManager = {
        cache: {}, 
        
        getHash(text) {
            let hash = 0, i, chr;
            if (text.length === 0) return hash;
            for (i = 0; i < text.length; i++) {
                chr = text.charCodeAt(i);
                hash = ((hash << 5) - hash) + chr;
                hash |= 0; 
            }
            return "h" + hash;
        },

        async translate(text, targetLang) {
            if (!text || targetLang === 'English') return text;
            const hash = this.getHash(text);
            
            if (!this.cache[hash]) this.cache[hash] = {};
            if (this.cache[hash][targetLang]) return this.cache[hash][targetLang];

            try {
                const res = await fetch('/api/translate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ text, language: targetLang })
                });
                const data = await res.json();
                if (data.translated_text) {
                    this.cache[hash][targetLang] = data.translated_text;
                    return data.translated_text;
                }
            } catch (e) {
                console.error("Translation fail:", e);
            }
            return text; 
        }
    };

    // --- Infinite Scroll Logic ---
    const track = document.getElementById('track');
    const container = document.getElementById('suggestion-carousel');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    
    if (track && container) {
        const originalCards = Array.from(track.children);
        const cardWidth = originalCards[0].offsetWidth + 20; // Width + Gap
        
        // Clone cards for seamless looping (Triple the set for smooth bidirectional)
        // Prepend and Append copies
        originalCards.forEach(card => track.appendChild(card.cloneNode(true)));
        originalCards.forEach(card => track.appendChild(card.cloneNode(true))); 

        // Auto Scroll Variables
        let scrollSpeed = 0.5; 
        const baseSpeed = 0.5;
        let isHovered = false;
        let isDragging = false;
        let startX;
        let scrollLeftStart;

        // One-time centering (optional, or just start at 0)
        // container.scrollLeft = 0; 
        
        const scrollLoop = () => {
            if (!isHovered && !isDragging) {
                container.scrollLeft += scrollSpeed;
            }
            
            // Seamless Reset Logic
            // If scrolled past the first set (original + clone1 + clone2)
            // We want to reset when we reach the end of the *second* set effectively
            const maxScroll = track.scrollWidth / 3; 

            // If we scrolled past the first set (which is now at the start), reset
            if (container.scrollLeft >= maxScroll * 2) {
                container.scrollLeft = maxScroll;
            } 
            // If we backward scrolled to start
            else if (container.scrollLeft <= 0) {
                container.scrollLeft = maxScroll;
            }

            requestAnimationFrame(scrollLoop);
        };
        
        // Start Loop
        requestAnimationFrame(scrollLoop);

        // Pause on Hover
        const stopAutoScroll = () => isHovered = true;
        const startAutoScroll = () => isHovered = false;
        
        container.addEventListener('mouseenter', stopAutoScroll);
        container.addEventListener('mouseleave', startAutoScroll);
        
        // Manual Drag Logic
        container.addEventListener('mousedown', (e) => {
            isDragging = true;
            isHovered = true; // Also pause auto
            startX = e.pageX - container.offsetLeft;
            scrollLeftStart = container.scrollLeft;
            container.style.cursor = 'grabbing';
        });

        container.addEventListener('mouseleave', () => {
            isDragging = false;
            isHovered = false;
            container.style.cursor = 'grab';
        });

        container.addEventListener('mouseup', () => {
            isDragging = false;
            isHovered = true; // Keep hovered if still inside
            container.style.cursor = 'grab';
        });

        container.addEventListener('mousemove', (e) => {
            if (!isDragging) return;
            e.preventDefault();
            const x = e.pageX - container.offsetLeft;
            const walk = (x - startX) * 2; // Scroll-fast
            container.scrollLeft = scrollLeftStart - walk;
        });

        // Navigation Buttons
        if (prevBtn && nextBtn) {
            prevBtn.addEventListener('click', () => {
                container.scrollBy({ left: -300, behavior: 'smooth' });
            });
            nextBtn.addEventListener('click', () => {
                container.scrollBy({ left: 300, behavior: 'smooth' });
            });
        }

        // Mouse Wheel Horizontal Scroll
        container.addEventListener('wheel', (e) => {
            e.preventDefault();
            // Scroll faster than default for better feel
            container.scrollLeft += e.deltaY;
            // Also support native horizontal scroll devices (trackpads)
            container.scrollLeft += e.deltaX;
            
            // Interaction pause logic
            isHovered = true;
            clearTimeout(window.hoverTimeout);
            window.hoverTimeout = setTimeout(() => {
                 if (!container.matches(':hover')) isHovered = false;
            }, 1000);
        });
    }

    // --- Language Switching ---
    // Language Configuration with BCP-47 codes for Speech-to-Text
    const LANGUAGES = [
        { code: 'English', native: 'English', bcp47: 'en-IN' },
        { code: 'Hindi', native: 'हिंदी', bcp47: 'hi-IN' },
        { code: 'Gujarati', native: 'ગુજરાતી', bcp47: 'gu-IN' },
        { code: 'Marathi', native: 'मराठी', bcp47: 'mr-IN' },
        { code: 'Bengali', native: 'বাংলা', bcp47: 'bn-IN' },
        { code: 'Tamil', native: 'தமிழ்', bcp47: 'ta-IN' },
        { code: 'Telugu', native: 'తెలుగు', bcp47: 'te-IN' },
        { code: 'Kannada', native: 'ಕನ್ನಡ', bcp47: 'kn-IN' },
        { code: 'Malayalam', native: 'മലയാളം', bcp47: 'ml-IN' },
        { code: 'Punjabi', native: 'ਪੰਜਾਬੀ', bcp47: 'pa-IN' }
    ];

    // Check localStorage for saved language or default to English
    let currentLanguage = localStorage.getItem('user_language') || 'English';
    let isLanguageSwitching = false;

    // Render Dropdown
    const renderLanguageDropdown = () => {
        const list = document.getElementById('language-list');
        if (!list) return;
        
        list.innerHTML = LANGUAGES.map(lang => `
            <li>
                <button class="dropdown-item d-flex justify-content-between align-items-center" 
                        type="button" 
                        id="lang-btn-${lang.code}" 
                        onclick="changeLanguage('${lang.code}')">
                    <span>${lang.code} <small class="text-secondary ms-1">(${lang.native})</small></span>
                    <i class="fas fa-check text-success ms-2 ${currentLanguage === lang.code ? '' : 'd-none'}" id="check-${lang.code}"></i>
                </button>
            </li>
        `).join('');
    };

    window.toggleLangMenu = () => {
        const menu = document.getElementById('lang-menu');
        if (menu) {
            menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
        }
    };

    window.selectLanguage = (lang) => {
        // This function is still used by logic elsewhere if needed, 
        // though UI is mostly in settings now.
        const menu = document.getElementById('lang-menu');
        const label = document.getElementById('current-lang');
        if (menu) menu.style.display = 'none';
        if (label) label.textContent = lang;
        changeLanguage(lang);
    };
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        const menu = document.getElementById('lang-menu');
        const btn = document.getElementById('lang-btn');
        if (menu && btn && !menu.contains(e.target) && !btn.contains(e.target)) {
            menu.style.display = 'none';
        }
    });

    // Helper: Update visual indicators
    const updateLanguageUI = (lang) => {
        LANGUAGES.forEach(l => {
            const btn = document.getElementById(`lang-btn-${l.code}`);
            const check = document.getElementById(`check-${l.code}`);
            if (btn && check) {
                if (l.code === lang) {
                    btn.classList.add('active');
                    check.classList.remove('d-none');
                } else {
                    btn.classList.remove('active');
                    check.classList.add('d-none');
                }
            }
        });
    };

    window.changeLanguage = async (lang) => {
        if (isLanguageSwitching) {
            console.warn("Language switch already in progress. Ignoring.");
            return;
        }
        if (lang === currentLanguage) return;

        console.log(`[Language Switch] Starting switch to: ${lang}`);
        isLanguageSwitching = true;
        
        // Stop any active TTS when switching language
        if (typeof stopSpeaking === 'function') stopSpeaking();
        
        try {
            currentLanguage = lang;
            localStorage.setItem('user_language', lang); // Persist selection
            
            // Optimistic Session Update (Non-blocking)
            fetch('/change-language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ language: lang, session_id: sessionId })
            }).catch(err => console.error("Session Update Failed", err));

            // Update UI Label
            const label = document.getElementById('current-lang');
            if (label) {
                 const spinner = '<i class="fas fa-spinner fa-spin ms-1"></i>';
                 label.innerHTML = `${lang} ${spinner}`;
            }

            // Parallel Translation of existing bubbles
            const bubbles = document.querySelectorAll('.message-bubble');
            const tasks = Array.from(bubbles).map(async (bubble) => {
                const originalText = bubble.getAttribute('data-original-text');
                const role = bubble.getAttribute('data-role');
                
                if (originalText) {
                    const translated = await TranslationManager.translate(originalText, lang);
                    const contentContainer = bubble.querySelector('.message-content');
                    
                    if (contentContainer) {
                        if (role === 'assistant') {
                            contentContainer.innerHTML = marked.parse(translated);
                        } else {
                            contentContainer.textContent = translated;
                        }
                        
                        // Re-apply link attributes
                        const links = contentContainer.querySelectorAll('a');
                        links.forEach(link => {
                            link.setAttribute('target', '_blank');
                            link.setAttribute('rel', 'noopener noreferrer');
                        });
                    }

                    // Update Speak button onclick handler with new text and lang
                    const speakBtn = bubble.querySelector('.speak-btn');
                    if (speakBtn) {
                        speakBtn.onclick = () => window.toggleSpeech(speakBtn, translated, lang);
                    }
                }
            });

            await Promise.all(tasks);
            console.log(`[Language Switch] Completed switch to: ${lang}`);
            
            updateLanguageUI(lang); // Update indicators

            if (label) label.textContent = lang;
            scrollToBottom();
            
        } catch (error) {
            console.error("[Language Switch] Error:", error);
            alert("Error switching language. Please try again.");
        } finally {
            isLanguageSwitching = false;
        }
    };

    // Fetch Scheme Details for Chat
    window.fetchSchemeDetails = async (schemeName) => {
        // Use global currentLanguage
        
        // Show typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing';
        typingDiv.className = 'ms-3 mb-3';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        chatBox.appendChild(typingDiv);
        scrollToBottom();

        try {
            const res = await fetch('/scheme-details', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    scheme_name: schemeName, 
                    session_id: sessionId,
                    language: currentLanguage 
                })
            });
            const data = await res.json();
            
            // Remove typing indicator
            if(document.getElementById('typing')) document.getElementById('typing').remove();

            if (data.error) {
                renderAssistantMessage(`Error: ${data.error}`);
            } else {
                renderAssistantMessage(data.response);
            }
        } catch (err) {
            console.error(err);
            if(document.getElementById('typing')) document.getElementById('typing').remove();
            toggleLogoProcessing(false);
            renderAssistantMessage("Sorry, I encountered an error. Please try again.");
        }
    };

    // Store schemes globally for search filtering
    let recommendationState = { mode: 'default', schemes: [], allSchemes: [] };
    
    // Compare Feature State
    window.selectedSchemesForComparison = [];

    window.toggleCategorySchemeComparison = (schemeId, checkboxElem) => {
        if (checkboxElem.checked) {
            if (window.selectedSchemesForComparison.length >= 2) {
                alert("You can only compare a maximum of 2 schemes at a time.");
                checkboxElem.checked = false;
                return;
            }
            if (!window.selectedSchemesForComparison.includes(schemeId)) {
                window.selectedSchemesForComparison.push(schemeId);
            }
        } else {
            window.selectedSchemesForComparison = window.selectedSchemesForComparison.filter(id => id !== schemeId);
        }
        
        const btn = document.getElementById('modal-compare-action-btn');
        if (btn) {
            if (window.selectedSchemesForComparison.length === 2) {
                btn.disabled = false;
            } else {
                btn.disabled = true;
            }
        }
    };

    window.openCompareModal = async () => {
        // Reset selections and UI state locally
        window.selectedSchemesForComparison = [];
        
        const actionBtn = document.getElementById('modal-compare-action-btn');
        if(actionBtn) actionBtn.disabled = true;
        
        document.getElementById('compare-category-select').innerHTML = '<option value="" selected disabled>Loading categories...</option>';
        document.getElementById('compare-modal-checkboxes').innerHTML = '<div class="text-secondary small fst-italic py-2 text-center opacity-75">Please choose a category above to view schemes.</div>';
        
        window.showCompareSelectionScreen();
        
        const modal = new bootstrap.Modal(document.getElementById('compareModal'));
        modal.show();

        try {
            // Fetch all schemes
            const res = await fetch('/api/schemes/all');
            const data = await res.json();
            const schemes = data.schemes || [];
            
            // Extract distinct categories
            const categories = [...new Set(schemes.map(s => s.category).filter(c => c))].sort();
            
            const selectHTML = ['<option value="" selected disabled>Select a category</option>']
                .concat(categories.map(c => `<option value="${c}">${c}</option>`)).join('');
                
            document.getElementById('compare-category-select').innerHTML = selectHTML;
            
            // Store fetched schemes to avoid re-fetching on change
            window._allModalSchemes = schemes;
            
        } catch(e) {
            console.error("Failed to fetch schemes for compare modal:", e);
            document.getElementById('compare-category-select').innerHTML = '<option value="" selected disabled>Error loading categories.</option>';
        }
    };
    
    window.renderCompareCategorySchemes = () => {
        const select = document.getElementById('compare-category-select');
        const cat = select.value;
        const container = document.getElementById('compare-modal-checkboxes');
        
        if (!cat || !window._allModalSchemes) {
            container.innerHTML = '<div class="text-secondary small fst-italic py-2 text-center opacity-75">Please select a category above.</div>';
            return;
        }
        
        // Filter schemes by category and render checkboxes
        const filtered = window._allModalSchemes.filter(s => s.category === cat);
        
        window.selectedSchemesForComparison = []; // reset selected when switching category
        const actionBtn = document.getElementById('modal-compare-action-btn');
        if(actionBtn) actionBtn.disabled = true;
        
        if (filtered.length === 0) {
            container.innerHTML = '<div class="text-secondary small fst-italic py-2 text-center opacity-75">No schemes found for this category.</div>';
            return;
        }

        const boxesHTML = filtered.map(s => {
            return `
                <div class="d-flex align-items-center justify-content-between p-3 border rounded-3 theme-border-subtle theme-bg-surface">
                    <div>
                        <div class="fw-bold theme-text-primary small mb-1">${s.name}</div>
                        <div class="text-secondary opacity-75" style="font-size: 0.70rem; line-height: 1.2;">
                            ${s.description ? s.description.substring(0, 80) + '...' : 'No description.'}
                        </div>
                    </div>
                    <div class="form-check form-switch ms-3">
                        <input class="form-check-input flex-shrink-0" type="checkbox" id="modal-compare-chk-${s.id}" 
                            onchange="toggleCategorySchemeComparison(${s.id}, this)" style="cursor: pointer;">
                    </div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = boxesHTML;
    };
    
    window.showCompareSelectionScreen = () => {
        document.getElementById('compare-selection-screen').classList.remove('d-none');
        document.getElementById('compare-content').classList.add('d-none');
        document.getElementById('modal-compare-back-btn').classList.add('d-none');
        document.getElementById('modal-compare-action-btn').classList.remove('d-none');
    };

    window.compareSelectedSchemes = async () => {
        if (window.selectedSchemesForComparison.length !== 2) return;
        
        const loading = document.getElementById('compare-loading');
        const content = document.getElementById('compare-content');
        const tBody = document.getElementById('compare-table-body');
        const selectionScreen = document.getElementById('compare-selection-screen');
        const backBtn = document.getElementById('modal-compare-back-btn');
        const actionBtn = document.getElementById('modal-compare-action-btn');
        
        if (selectionScreen) selectionScreen.classList.add('d-none');
        if (actionBtn) actionBtn.classList.add('d-none');
        
        loading.classList.remove('d-none');
        content.classList.add('d-none');
        
        try {
            const res = await fetch('/api/schemes/compare', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ scheme_ids: window.selectedSchemesForComparison })
            });
            const data = await res.json();
            
            if (data.comparison) {
                const cmp = data.comparison;
                
                document.getElementById('compare-scheme-1-title').textContent = cmp["Name"][0];
                document.getElementById('compare-scheme-2-title').textContent = cmp["Name"][1];
                
                let rowsHtml = '';
                const features = ["Category", "Benefit Summary", "Target Age", "Income Limit", "Occupation", "State"];
                
                features.forEach(feature => {
                    const val1 = cmp[feature][0] || "N/A";
                    const val2 = cmp[feature][1] || "N/A";
                    
                    rowsHtml += `
                        <tr>
                            <td class="fw-bold theme-text-secondary small">${feature}</td>
                            <td class="theme-text-primary fs-6">${val1}</td>
                            <td class="theme-text-primary fs-6">${val2}</td>
                        </tr>
                    `;
                });
                
                tBody.innerHTML = rowsHtml;
            }
        } catch (e) {
            console.error(e);
            tBody.innerHTML = '<tr><td colspan="3" class="text-danger text-center">Failed to load comparison data.</td></tr>';
        } finally {
            loading.classList.add('d-none');
            content.classList.remove('d-none');
            const backBtn = document.getElementById('modal-compare-back-btn');
            if(backBtn) backBtn.classList.remove('d-none');
        }
    };

    const renderSchemes = () => {
        const container = document.getElementById('recommendations-box');
        const schemesUrl = recommendationState.schemes;
        const mode = recommendationState.mode;
        
        // Show banner ONLY when we are explicitly in "fallback" mode from the server.
        let headerMessage = '';
        if (mode === 'fallback') {
            headerMessage = `<div class="text-warning small mb-3 fw-bold"><i class="fas fa-info-circle me-1"></i> No exact match found. Showing all available schemes.</div>`;
        }

        if (!schemesUrl || schemesUrl.length === 0) {
            container.innerHTML = `<div class="text-secondary small fst-italic mt-2">No schemes available.</div>`;
            return;
        }

        const cardsHTML = schemesUrl.map(s => {
            const isEligible = s.eligibility_status === 'Eligible';
            const isPartial = s.eligibility_status === 'Check Criteria';
            
            let badgeBg = isEligible ? 'rgba(0,230,118,0.1)' : (isPartial ? 'rgba(255,193,7,0.1)' : 'rgba(108,117,125,0.1)');
            let badgeColor = isEligible ? 'var(--accent-green, #00E676)' : (isPartial ? '#ffc107' : '#6c757d');
            let badgeText = s.eligibility_status ? s.eligibility_status.toUpperCase() : (isEligible ? 'ELIGIBLE' : 'VIEW');
            
            const collapseId = `explain-${s.id || s.name.replace(/[^a-zA-Z0-9]/g, '')}`;
            
            let rulesHtml = '';
            if (s.matched_rules && s.matched_rules.length > 0) {
                rulesHtml = s.matched_rules.map(r => `
                    <div class="d-flex align-items-center mb-1">
                        <i class="fas fa-check-circle text-success me-2" style="font-size: 0.8rem;"></i>
                        <span class="theme-text-secondary" style="font-size: 0.75rem;">${r}</span>
                    </div>
                `).join('');
            } else {
                rulesHtml = '<div class="text-secondary small fst-italic">Review official criteria for details.</div>';
            }

            return `
                <div class="rec-card-modern" onclick="fetchSchemeDetails('${s.name}')" style="height: auto; min-height: 220px; padding-bottom: 1rem;">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="theme-text-primary fw-bold" style="font-size: 0.95rem;">${s.name}</div>
                        <span class="badgex" style="font-size: 0.6rem; background: ${badgeBg}; color: ${badgeColor}; padding: 2px 6px; border-radius: 4px; white-space: nowrap; margin-left: 8px;">${badgeText}</span>
                    </div>
                    <div class="text-secondary small mb-3" style="font-size: 0.8rem; line-height: 1.4;">
                        ${s.description ? s.description.substring(0, 60) + '...' : 'No description.'}
                    </div>
                    
                    <div class="mt-auto mb-3">
                        <a class="text-decoration-none small" style="cursor: pointer; font-size: 0.75rem; font-weight: 600; color: var(--accent-primary);" data-bs-toggle="collapse" data-bs-target="#${collapseId}" onclick="event.stopPropagation()">
                            Why You're Eligible <i class="fas fa-chevron-down ms-1" style="font-size: 0.7em;"></i>
                        </a>
                        <div class="collapse mt-2 pt-2 border-top theme-border-subtle" id="${collapseId}" onclick="event.stopPropagation()">
                            ${rulesHtml}
                        </div>
                    </div>

                    <div class="d-flex justify-content-between align-items-center mt-auto">
                        <div class="text-secondary" style="font-size: 0.75rem;">
                            <i class="fas ${getCategoryIcon(s.category)} me-1"></i> ${s.category}
                        </div>
                        <a href="${s.official_link || '#'}" 
                           target="_blank" 
                           rel="noopener noreferrer" 
                           class="text-decoration-none theme-text-primary small"
                           onclick="event.stopPropagation()"
                           style="font-size: 0.75rem; opacity: 0.7; transition: opacity 0.2s;">
                            View <i class="fas fa-external-link-alt ms-1"></i>
                        </a>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = headerMessage + cardsHTML;
    };

    // Fetch All Schemes (Default State)
    const fetchAllSchemes = async () => {
        try {
            const res = await fetch('/api/schemes/all');
            const data = await res.json();
            recommendationState.allSchemes = data.schemes || [];
            
            // If we are in default mode (no chat messages), populate schemes as well
            if (recommendationState.mode === 'default') {
                recommendationState.schemes = [...recommendationState.allSchemes];
                renderSchemes();
            }
        } catch (e) {
            console.error("Error fetching all schemes:", e);
        }
    };

    // Fetch Recommendations
    const fetchRecommendations = async () => {
        try {
            // Pass session_id to get intent-based recommendations
            const res = await fetch(`/api/recommendations?session_id=${sessionId || ''}`);
            const data = await res.json();
            
            // Parse response structure
            if (Array.isArray(data)) {
                recommendationState.schemes = data;
                // If it's an old array format and chat hasn't started, it's default
                const hasChatMessages = chatBox.querySelectorAll('.message-bubble').length > 0;
                recommendationState.mode = hasChatMessages ? 'filtered' : 'default';
            } else {
                recommendationState.schemes = data.schemes || [];
                const hasChatMessages = chatBox.querySelectorAll('.message-bubble').length > 0;
                recommendationState.mode = hasChatMessages ? (data.mode || 'filtered') : 'default';
            }
            
            renderSchemes();
            
            // UX: Expand Recommendations section if results are interesting/filtered
            if (recommendationState.mode !== 'default' && recommendationState.schemes.length > 0) {
                const recCollapse = document.getElementById('collapseRecs');
                if (recCollapse && !recCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(recCollapse, { toggle: false });
                    bsCollapse.show();
                }
            }
            
        } catch (e) {
            console.error("Error fetching recommendations:", e);
        }
    };

    // Search Filter Logic
    const searchInput = document.getElementById('scheme-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            
            // UX: Auto-expand Recommendations section when searching
            if (term.length > 0) {
                const recCollapse = document.getElementById('collapseRecs');
                if (recCollapse && !recCollapse.classList.contains('show')) {
                    const bsCollapse = new bootstrap.Collapse(recCollapse, { toggle: false });
                    bsCollapse.show();
                }
            }

            // If searching, search EVERYTHING. If cleared, go back to RECOMMENDATIONS.
            const sourceSchemes = term.length > 0 ? recommendationState.allSchemes : recommendationState.schemes;

            const filtered = sourceSchemes.filter(s => 
                s.name.toLowerCase().includes(term) || 
                s.category.toLowerCase().includes(term) ||
                (s.target_group && s.target_group.toLowerCase().includes(term))
            );
            
            // Temporarily trick renderSchemes by overriding schemes pointer without changing the global mode
            const container = document.getElementById('recommendations-box');
            // Duplicate the render logic minimally here for search without mutating real state
            
            let headerMessage = '';
            if (recommendationState.mode === 'fallback') {
                headerMessage = `<div class="text-warning small mb-3 fw-bold"><i class="fas fa-info-circle me-1"></i> No exact match found. Showing all available schemes.</div>`;
            }

            if (!filtered || filtered.length === 0) {
                container.innerHTML = headerMessage + `<div class="text-secondary small fst-italic mt-2">No matching schemes.</div>`;
                return;
            }

            const cardsHTML = filtered.map(s => {
                const isEligible = s.eligibility_status === 'Eligible';
                const isPartial = s.eligibility_status === 'Check Criteria';
                
                let badgeBg = isEligible ? 'rgba(0,230,118,0.1)' : (isPartial ? 'rgba(255,193,7,0.1)' : 'rgba(108,117,125,0.1)');
                let badgeColor = isEligible ? 'var(--accent-green, #00E676)' : (isPartial ? '#ffc107' : '#6c757d');
                let badgeText = s.eligibility_status ? s.eligibility_status.toUpperCase() : (isEligible ? 'ELIGIBLE' : 'VIEW');
                
                const collapseId = `search-explain-${s.id || s.name.replace(/[^a-zA-Z0-9]/g, '')}`;
                
                let rulesHtml = '';
                if (s.matched_rules && s.matched_rules.length > 0) {
                    rulesHtml = s.matched_rules.map(r => `
                        <div class="d-flex align-items-center mb-1">
                            <i class="fas fa-check-circle text-success me-2" style="font-size: 0.8rem;"></i>
                            <span class="theme-text-secondary" style="font-size: 0.75rem;">${r}</span>
                        </div>
                    `).join('');
                } else {
                    rulesHtml = '<div class="text-secondary small fst-italic">Review official criteria for details.</div>';
                }

                return `
                    <div class="rec-card-modern" onclick="fetchSchemeDetails('${s.name}')" style="height: auto; min-height: 220px; padding-bottom: 1rem;">
                        <div class="d-flex justify-content-between align-items-start mb-2">
                            <div class="theme-text-primary fw-bold" style="font-size: 0.95rem;">${s.name}</div>
                            <span class="badgex" style="font-size: 0.6rem; background: ${badgeBg}; color: ${badgeColor}; padding: 2px 6px; border-radius: 4px; white-space: nowrap; margin-left: 8px;">${badgeText}</span>
                        </div>
                        <div class="text-secondary small mb-3" style="font-size: 0.8rem; line-height: 1.4;">
                            ${s.description ? s.description.substring(0, 60) + '...' : 'No description.'}
                        </div>
                        
                        <div class="mt-auto mb-3">
                            <a class="text-decoration-none small" style="cursor: pointer; font-size: 0.75rem; font-weight: 600; color: var(--accent-primary);" data-bs-toggle="collapse" data-bs-target="#${collapseId}" onclick="event.stopPropagation()">
                                Why You're Eligible <i class="fas fa-chevron-down ms-1" style="font-size: 0.7em;"></i>
                            </a>
                            <div class="collapse mt-2 pt-2 border-top theme-border-subtle" id="${collapseId}" onclick="event.stopPropagation()">
                                ${rulesHtml}
                            </div>
                        </div>

                        <div class="d-flex justify-content-between align-items-center mt-auto">
                            <div class="theme-text-secondary" style="font-size: 0.75rem;">
                                <i class="fas ${getCategoryIcon(s.category)} me-1"></i> ${s.category}
                            </div>
                            <a href="${s.official_link || '#'}" target="_blank" rel="noopener noreferrer" class="text-decoration-none theme-text-primary small" onclick="event.stopPropagation()">View <i class="fas fa-external-link-alt ms-1"></i></a>
                        </div>
                    </div>
                `;
            }).join('');
            container.innerHTML = headerMessage + cardsHTML;
        });
    }

    // Call on load
    const renderSettingsLanguageDropdown = () => {
        const select = document.getElementById('setting-language-select');
        if (!select) return;
        select.innerHTML = LANGUAGES.map(lang => 
            `<option value="${lang.code}" ${currentLanguage === lang.code ? 'selected' : ''}>${lang.native} - ${lang.code}</option>`
        ).join('');
    };
    
    renderLanguageDropdown(); // legacy
    renderSettingsLanguageDropdown();
    updateLanguageUI(currentLanguage); // Set initial active state
    if(currentLanguage !== 'English') {
        // Update label immediately if saved language is not English
        const label = document.getElementById('current-lang');
        if (label) label.textContent = currentLanguage;
    }

    // Initial Load: Show all schemes as default
    fetchAllSchemes();
    
    // 6. Close Modal
    const modalEl = document.getElementById('newChatModal');
    if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    }

    // Store current profile globally
    let currentProfileData = {};

    // --- Text-to-Speech (TTS) State ---
    let currentUtterance = null;
    let currentSpeakBtn = null;
    let availableVoices = [];

    // Pre-load voices (Async in some browsers)
    const loadVoices = () => {
        if (!window.speechSynthesis) return;
        availableVoices = window.speechSynthesis.getVoices();
    };
    
    // Listen for voices ready event
    if (window.speechSynthesis) {
        loadVoices();
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = loadVoices;
        }
    }

    const stopSpeaking = () => {
        if (window.speechSynthesis) {
            window.speechSynthesis.cancel();
        }
        if (currentSpeakBtn) {
            currentSpeakBtn.classList.remove('speaking');
            currentSpeakBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
            currentSpeakBtn = null;
        }
        currentUtterance = null;
    };

    // Helper to find the best voice across browsers/platforms
    const getBestVoice = (bcp47) => {
        if (!availableVoices.length) loadVoices();
        
        // 1. Exact BCP-47 match (e.g., 'hi-IN')
        let regexExact = new RegExp(`^${bcp47.replace('-', '[-_]')}$`, 'i');
        let voice = availableVoices.find(v => regexExact.test(v.lang));
        
        // 2. Try prefix match specifically preferring Google/Premium (e.g., 'hi')
        if (!voice) {
            const prefix = bcp47.split('-')[0];
            const prefixMatches = availableVoices.filter(v => v.lang.toLowerCase().startsWith(prefix.toLowerCase()));
            
            if (prefixMatches.length > 0) {
                // Prefer 'Google' or voices that don't sound completely robotic if available
                voice = prefixMatches.find(v => v.name.includes('Google') || v.name.includes('Premium')) || prefixMatches[0];
            }
        }
        
        return voice;
    };

    window.toggleSpeech = (btnElement, textToSpeak, langCode) => {
        if (!window.speechSynthesis) {
            alert("Text-to-Speech is not supported in this browser.");
            return;
        }

        // If clicking the currently playing button -> Stop
        if (currentSpeakBtn === btnElement) {
            stopSpeaking();
            return;
        }

        // Stop any existing speech
        stopSpeaking();

        // Start new speech visually
        currentSpeakBtn = btnElement;
        currentSpeakBtn.classList.add('speaking');
        currentSpeakBtn.innerHTML = '<i class="fas fa-volume-up fa-fade"></i>';

        // Map internal language state to correct BCP-47 or fallback
        const langObj = LANGUAGES.find(l => l.code === langCode);
        const bcp47 = langObj ? langObj.bcp47 : 'en-IN';

        // Clean Text: Strip HTML, markdown astersisks, hash marks, underscores
        let cleanText = textToSpeak.replace(/<[^>]+>/g, ' '); // remove HTML
        cleanText = cleanText.replace(/[*#_`]/g, '');         // remove markdown symbols
        cleanText = cleanText.replace(/\n\s*\n/g, '. ');      // treat multiple newlines as full stops
        
        currentUtterance = new SpeechSynthesisUtterance(cleanText);
        currentUtterance.lang = bcp47;
        currentUtterance.rate = 1.0;
        
        // Attempt to select the highest quality matching voice
        const bestVoice = getBestVoice(bcp47);
        if (bestVoice) {
            currentUtterance.voice = bestVoice;
        }

        currentUtterance.onend = () => {
            stopSpeaking();
        };

        currentUtterance.onerror = (e) => {
            console.error("SpeechSynthesis Error:", e);
            stopSpeaking();
        };

        window.speechSynthesis.speak(currentUtterance);
    };

    // Helper to capture profile update from chat response
    const updateProfileGlobals = (profile) => {
        currentProfileData = profile;
    };

    const toggleLogoProcessing = (isProcessing) => {
        const logo = document.getElementById('main-ai-logo');
        if (logo) {
            if (isProcessing) logo.classList.add('processing');
            else logo.classList.remove('processing');
        }
    };

    const renderUserMessage = (content) => {
        // Hide Hero Section on first message
        const hero = document.getElementById('hero-section');
        if (hero) hero.style.display = 'none';

        const div = document.createElement('div');
        div.className = `d-flex w-100 mb-3 justify-content-end`;
        
        const bubble = document.createElement('div');
        bubble.className = `message-bubble message-user`;
        
        // Store Meta
        bubble.setAttribute('data-original-text', content);
        bubble.setAttribute('data-role', 'user');

        const contentContainer = document.createElement('div');
        contentContainer.className = 'message-content';
        contentContainer.textContent = content;

        bubble.appendChild(contentContainer);
        div.appendChild(bubble);
        chatBox.appendChild(div);
        
        scrollToBottom();
    };

    const renderAssistantMessage = async (content) => {
        // Hide Hero Section on first message
        const hero = document.getElementById('hero-section');
        if (hero) hero.style.display = 'none';

        const div = document.createElement('div');
        div.className = `d-flex w-100 mb-3 justify-content-start`;
        
        const bubble = document.createElement('div');
        bubble.className = `message-bubble message-ai`;
        
        // Store Meta
        bubble.setAttribute('data-original-text', content);
        bubble.setAttribute('data-role', 'assistant');

        const contentContainer = document.createElement('div');
        contentContainer.className = 'message-content';

        let ttsText = content; 

        // Initial Render (English / Original)
        contentContainer.innerHTML = marked.parse(content);

        bubble.appendChild(contentContainer);
        div.appendChild(bubble);
        chatBox.appendChild(div);
        
        // Force links
        const applyLinks = () => {
            const links = contentContainer.querySelectorAll('a');
            links.forEach(link => {
                link.setAttribute('target', '_blank');
                link.setAttribute('rel', 'noopener noreferrer');
            });
        };
        applyLinks();
        scrollToBottom();

        // Check Translation
        if (currentLanguage !== 'English') {
            const translated = await TranslationManager.translate(content, currentLanguage);
            ttsText = translated;
            contentContainer.innerHTML = marked.parse(translated);
            applyLinks();
        }

        // Add Speech Button for Assistant 
        const speakBtn = document.createElement('button');
        speakBtn.className = 'speak-btn';
        speakBtn.innerHTML = '<i class="fas fa-volume-up"></i>';
        speakBtn.title = "Read aloud";
        
        // Add click event for manual TTS trigger
        speakBtn.onclick = () => window.toggleSpeech(speakBtn, ttsText, currentLanguage);
        
        // Append button to the message bubble
        bubble.appendChild(speakBtn);

        
        // Auto-TTS Feature Check
        if (userPreferences.autoTts) {
            window.toggleSpeech(speakBtn, ttsText, currentLanguage);
        }
    };

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Add User Message
        renderUserMessage(message);
        userInput.value = '';
        userInput.disabled = true;

        // Show animated typing indicator
        const typingDiv = document.createElement('div');
        typingDiv.id = 'typing';
        typingDiv.className = 'ms-3 mb-3';
        typingDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
        chatBox.appendChild(typingDiv);
        scrollToBottom();
        toggleLogoProcessing(true);

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, session_id: sessionId, language: currentLanguage })
            });

            const data = await response.json();
            
            // Remove typing indicator
            document.getElementById('typing').remove();
            toggleLogoProcessing(false);

            if (data.error) {
                renderAssistantMessage(`Error: ${data.error}`);
            } else {
                renderAssistantMessage(data.response);
                
                // Update Session
                if (data.session_id) {
                    const isNew = (sessionId !== data.session_id);
                    sessionId = data.session_id;
                    localStorage.setItem('chat_session_id', sessionId);
                    
                    // If it was the first message in a new session, refresh history titles
                    if (isNew || chatBox.querySelectorAll('.message-bubble').length <= 2) {
                        loadSessions();
                    }
                }
                
                // Update Profile Logic Removed
                if (data.profile) {
                    // Profile update from chat is still useful for context, 
                    // but visual display update is kept minimal.
                    updateProfileGlobals(data.profile); 
                    const p = data.profile;
                    const summary = [p.age, p.occupation, p.state].filter(Boolean).join(', ');
                    if(profileDisplay) profileDisplay.textContent = summary || 'None yet';
                    
                    fetchRecommendations();
                }
            }

        } catch (err) {
            document.getElementById('typing').remove();
            renderAssistantMessage('Network Error. Is the backend running?');
            console.error(err);
        } finally {
            userInput.disabled = false;
            userInput.focus();
        }
    });

    // --- Infinite Native Scroll Logic Removed (consolidated at top) ---

    // New Chat Confirmation
    window.startNewChat = () => {
        const modal = new bootstrap.Modal(document.getElementById('newChatModal'));
        modal.show();
    };

    window.confirmNewChat = () => {
        // Clear Frontend State
        localStorage.removeItem('chat_session_id');
        sessionId = null;
        currentProfileData = {};

        // Stop any active TTS
        if (typeof stopSpeaking === 'function') stopSpeaking();

        // Remove only messages, keep hero section
        const messages = chatBox.querySelectorAll('.d-flex.w-100.mb-3');
        messages.forEach(msg => msg.remove());
        
        // Reset Profile Display (if exists)
        const pDisplay = document.getElementById('profile-display');
        if(pDisplay) {
            pDisplay.innerHTML = '<i class="fas fa-user-circle fs-5 text-secondary"></i><span class="small">Guest</span>';
        }
        
        // Show Hero Section
        const hero = document.getElementById('hero-section');
        if(hero) {
            hero.style.display = 'block';
            hero.classList.add('animate-fade-up');
        }
        
        // Close Modal
        const modalEl = document.getElementById('newChatModal');
        const modal = bootstrap.Modal.getInstance(modalEl);
        if(modal) modal.hide();
        
        // Allow input
        userInput.disabled = false;
        userInput.focus();

        // Clear Backend Session
        fetch('/api/clear_chat', { method: 'POST' })
            .catch(err => console.error("Failed to clear backend session:", err));
        
        // Refresh recommendations (reset state strictly to default right away)
        recommendationState.mode = 'default';
        fetchAllSchemes();
    };

    // --- Voice Input (Speech-to-Text) ---
    const micBtn = document.getElementById('mic-btn');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let isListening = false;

    if (SpeechRecognition && micBtn) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = true; // Show results as they speak

        const stopListening = () => {
            if (isListening) {
                recognition.stop();
                isListening = false;
                micBtn.classList.remove('listening');
                userInput.placeholder = "Type your message here...";
            }
        };

        const startListening = () => {
             // Find matching BCP-47 code
             const langObj = LANGUAGES.find(l => l.code === currentLanguage);
             recognition.lang = langObj ? langObj.bcp47 : 'en-IN';

             try {
                recognition.start();
                isListening = true;
                micBtn.classList.add('listening');
                userInput.placeholder = `Listening in ${currentLanguage}... Speak now`;
             } catch (e) {
                console.error("Speech recognition error:", e);
                stopListening();
             }
        };

        micBtn.addEventListener('click', () => {
            if (isListening) {
                stopListening();
            } else {
                startListening();
            }
        });

        // Handle Results
        recognition.onresult = (event) => {
            // Overwrite the input with the latest speech result
            userInput.value = event.results[0][0].transcript;
        };

        // Handle Errors & End
        recognition.onerror = (event) => {
            console.error("Speech Recognition Error:", event.error);
            if (event.error === 'not-allowed') {
                 alert("Microphone permission denied. Please allow it in your browser settings.");
            }
            stopListening();
        };

        recognition.onend = () => {
            // Check if still marked active (unexpected stop)
            if (isListening) {
                stopListening();
            }
            // Auto focus back on input
            userInput.focus();
        };

        // Stop on form submit
        chatForm.addEventListener('submit', stopListening);

    } else if (micBtn) {
        // Hide if unsupported
        micBtn.style.display = 'none';
        console.warn("Speech recognition is not supported in this browser.");
    }

// --- User Profile Functions ---

async function saveProfileSettings() {
    const btn = document.getElementById('save-profile-btn');
    const originalText = btn.innerHTML;
    const spinner = `<i class="fas fa-spinner fa-spin"></i> Saving...`;
    
    btn.innerHTML = spinner;
    btn.disabled = true;

    const newName = document.getElementById('setting-name').value;
    
    // Prepare data
    const payload = {};
    if (newName) payload.full_name = newName;

    try {
        const res = await fetch('/api/user/profile', {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await res.json();
        
        if (res.ok) {
            // Update sidebar profile trigger dynamically without a full reload
            const sidebarAvatar = document.getElementById('sidebar-profile-avatar');
            if (sidebarAvatar) {
                sidebarAvatar.innerHTML = (data.full_name || 'U').charAt(0).toUpperCase();
            }
            
            // Update UI Name
            const profileInfoName = document.querySelector('.profile-info .fw-semibold');
            if (profileInfoName) profileInfoName.innerText = data.full_name;
            
            const profileMenuName = document.querySelector('.profile-menu .dropdown-item-text .fw-bold');
            if (profileMenuName) profileMenuName.innerText = data.full_name;
            
            btn.innerHTML = `<i class="fas fa-check"></i> Saved`;
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 2000);
            
        } else {
            alert("Failed to update profile: " + data.error);
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    } catch (e) {
        console.error(e);
        alert("An error occurred while saving profile.");
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

// --- Password Update Handling ---
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const currentPassword = document.getElementById('current_password').value;
            const newPassword = document.getElementById('new_password').value;
            const confirmPassword = document.getElementById('confirm_new_password').value;
            const alertBox = document.getElementById('password-alert');
            const btn = document.getElementById('change-pwd-btn');
            
            if (newPassword !== confirmPassword) {
                alertBox.textContent = "New passwords do not match!";
                alertBox.className = 'alert alert-danger mb-3';
                alertBox.classList.remove('d-none');
                return;
            }
            
            const originalText = btn.innerHTML;
            btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> Updating...`;
            btn.disabled = true;
            
            try {
                const res = await fetch('/api/user/password', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        current_password: currentPassword,
                        new_password: newPassword,
                        confirm_password: confirmPassword
                    })
                });
                
                const data = await res.json();
                
                if (res.ok) {
                    alertBox.textContent = data.message;
                    alertBox.className = 'alert alert-success mb-3';
                    alertBox.classList.remove('d-none');
                    changePasswordForm.reset();
                    
                    setTimeout(() => {
                        const modal = bootstrap.Modal.getInstance(document.getElementById('changePasswordModal'));
                        if (modal) modal.hide();
                        alertBox.classList.add('d-none');
                    }, 2000);
                } else {
                    alertBox.textContent = data.error || "Failed to update password";
                    alertBox.className = 'alert alert-danger mb-3';
                    alertBox.classList.remove('d-none');
                }
            } catch (err) {
                alertBox.textContent = "Connection error";
                alertBox.className = 'alert alert-danger mb-3';
                alertBox.classList.remove('d-none');
            } finally {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }
        });
    }

    // --- Eligibility Checker Submission ---
    const eligibilityForm = document.getElementById('eligibilityForm');
    if (eligibilityForm) {
        eligibilityForm.addEventListener('submit', handleEligibilitySubmit);
    }

    // Initial Load
    fetchRecommendations();
    loadSessions();
});

// --- Eligibility Checker Functions ---
async function handleEligibilitySubmit(e) {
    e.preventDefault();
    
    // UI Transitions
    const formContainer = document.getElementById('eligibility-form-container');
    const resultsContainer = document.getElementById('eligibility-results-container');
    const loadingState = document.getElementById('eligibility-results-loading');
    const contentState = document.getElementById('eligibility-results-content');
    
    formContainer.classList.add('d-none');
    resultsContainer.classList.remove('d-none');
    loadingState.classList.remove('d-none');
    contentState.classList.add('d-none');

    // Gather Form Data payload
    const payload = {
        age: parseInt(document.getElementById('elig-age').value),
        gender: document.getElementById('elig-gender').value,
        income: parseInt(document.getElementById('elig-income').value),
        occupation: document.getElementById('elig-occupation').value,
        state: document.getElementById('elig-state').value,
        category: document.getElementById('elig-category').value
    };

    try {
        const res = await fetch('/api/eligibility/check', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!res.ok) throw new Error('Network response was not ok');
        const data = await res.json();
        
        // Render JSON Response
        renderEligibilityResults(data);
        
        // Final UI Swaps
        loadingState.classList.add('d-none');
        contentState.classList.remove('d-none');

    } catch (err) {
        console.error("Eligibility Check Failed:", err);
        alert("There was an error calculating eligibility. Please try again.");
        resetEligibilityForm();
    }
}

function renderEligibilityResults(data) {
    // Inject Counts
    document.getElementById('count-eligible').innerText = data.eligible.length;
    document.getElementById('count-partial').innerText = data.partial.length;
    document.getElementById('count-not-eligible').innerText = data.not_eligible.length;
    
    // Build Lists
    const eligibleDiv = document.getElementById('results-eligible');
    const partialDiv = document.getElementById('results-partial');
    const notEligibleDiv = document.getElementById('results-not-eligible');
    
    eligibleDiv.innerHTML = data.eligible.length > 0 ? data.eligible.map(s => buildSchemeCard(s, 'eligible')).join('') : '<div class="text-secondary small fst-italic">No fully matched schemes found.</div>';
    partialDiv.innerHTML = data.partial.length > 0 ? data.partial.map(s => buildSchemeCard(s, 'partial')).join('') : '<div class="text-secondary small fst-italic">No partially matched schemes found.</div>';
    notEligibleDiv.innerHTML = data.not_eligible.length > 0 ? data.not_eligible.map(s => buildSchemeCard(s, 'not-eligible')).join('') : '<div class="text-secondary small fst-italic">No rejected schemes.</div>';
}

function buildSchemeCard(scheme, type) {
    const borderColor = type === 'eligible' ? 'border-success' : (type === 'partial' ? 'border-warning' : 'border-danger');
    const collapseId = `reasons-${scheme.id}`;
    
    // Build badges for reasons
    const reasonsHtml = scheme.reasons.map(r => `
        <div class="d-flex align-items-center mb-1">
            <i class="fas ${r.met ? 'fa-check text-success' : 'fa-times text-danger'} me-2"></i>
            <small class="theme-text-secondary">${r.detail}</small>
        </div>
    `).join('');

    return `
        <div class="card theme-bg-surface theme-text-primary ${borderColor} shadow-sm border-start border-4 border-top-0 border-bottom-0 border-end-0 border-opacity-75">
            <div class="card-body py-2 px-3">
                <h6 class="fw-bold mb-1">${scheme.name}</h6>
                <p class="small theme-text-secondary mb-2 lh-sm">${scheme.description}</p>
                <a class="text-decoration-none small" style="cursor: pointer;" data-bs-toggle="collapse" data-bs-target="#${collapseId}">
                    View Requirements <i class="fas fa-chevron-down ms-1" style="font-size: 0.75em;"></i>
                </a>
                <div class="collapse mt-2 pt-2 border-top theme-border-subtle" id="${collapseId}">
                    ${reasonsHtml}
                </div>
            </div>
        </div>
    `;
}

window.resetEligibilityForm = () => {
    // Resets visibility state back to Input Form
    const formContainer = document.getElementById('eligibility-form-container');
    const resultsContainer = document.getElementById('eligibility-results-container');
    
    if (formContainer && resultsContainer) {
        formContainer.classList.remove('d-none');
        resultsContainer.classList.add('d-none');
    }
};
