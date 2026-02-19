document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');
    const profileDisplay = document.getElementById('profile-display');

    let sessionId = localStorage.getItem('chat_session_id');

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
    // Store current language (default English)
    let currentLanguage = 'English';

    window.toggleLangMenu = () => {
        const menu = document.getElementById('lang-menu');
        if (menu) {
            menu.style.display = menu.style.display === 'none' ? 'block' : 'none';
        }
    };

    window.selectLanguage = (lang) => {
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

    window.changeLanguage = async (lang) => {
        if (lang === currentLanguage) return;
        currentLanguage = lang;
        
        // Show loading
        const originalText = chatBox.innerHTML;
        chatBox.innerHTML += `<div class="text-center text-muted small mt-2">Switching to ${lang}... <i class="fas fa-spinner fa-spin"></i></div>`;
        scrollToBottom();
        
        try {
            // 1. Tell Backend to Switch Language (No AI Generation)
            await fetch('/change-language', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    language: lang,
                    session_id: sessionId
                })
            });

            // 2. Translate History
            const res = await fetch('/api/translate_history', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    session_id: sessionId, 
                    language: lang 
                })
            });
            
            const data = await res.json();
            
            if (data.history) {
                // Clear and Re-render
                chatBox.innerHTML = '';
                
                if (data.history.length === 0) {
                     const hero = document.getElementById('hero-section');
                     if(hero) hero.style.display = 'block';
                } else {
                     const hero = document.getElementById('hero-section');
                     if(hero) hero.style.display = 'none';
                }

                data.history.forEach(msg => {
                    appendMessage(msg.role, msg.content);
                });
            }
        } catch (err) {
            console.error("Language switch error:", err);
            chatBox.innerHTML = originalText;
            alert("Error switching language.");
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
                appendMessage('assistant', `Error: ${data.error}`);
            } else {
                appendMessage('assistant', data.response);
            }
        } catch (e) {
            console.error(e);
            if(document.getElementById('typing')) document.getElementById('typing').remove();
            appendMessage('assistant', "Sorry, I couldn't fetch details for that scheme right now.");
        }
    };

    // Store schemes globally for search filtering
    let allSchemes = [];

    const renderSchemes = (schemesUrl) => {
        const container = document.getElementById('recommendations-box');
        
        if (schemesUrl.length === 0) {
            container.innerHTML = `<div class="text-secondary small fst-italic mt-2">No matching schemes.</div>`;
            return;
        }

        container.innerHTML = schemesUrl.map(s => {
            const isEligible = s.eligibility_status === 'Eligible';
            const badgeClass = isEligible ? 'rec-card-badge eligible' : 'rec-card-badge';
            
            return `
                <div class="rec-card-modern" onclick="fetchSchemeDetails('${s.name}')">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div class="text-white fw-bold" style="font-size: 0.95rem;">${s.name}</div>
                        <span class="badgex" style="font-size: 0.6rem; background: rgba(0,230,118,0.1); color: var(--accent-green); padding: 2px 6px; border-radius: 4px;">ELIGIBLE</span>
                    </div>
                    <div class="text-secondary small mb-3" style="font-size: 0.8rem; line-height: 1.4;">
                        ${s.description ? s.description.substring(0, 60) + '...' : 'No description.'}
                    </div>
                    <div class="d-flex justify-content-between align-items-center">
                        <div class="text-secondary" style="font-size: 0.75rem;">
                            <i class="fas ${getCategoryIcon(s.category)} me-1"></i> ${s.category}
                        </div>
                        <a href="${s.official_link || '#'}" 
                           target="_blank" 
                           rel="noopener noreferrer" 
                           class="text-decoration-none text-white small"
                           onclick="event.stopPropagation()"
                           style="font-size: 0.75rem; opacity: 0.7; transition: opacity 0.2s;">
                            View <i class="fas fa-external-link-alt ms-1"></i>
                        </a>
                    </div>
                </div>
            `;
        }).join('');
    };

    // Fetch Recommendations
    const fetchRecommendations = async () => {
        try {
            // Pass session_id to get intent-based recommendations
            const res = await fetch(`/api/recommendations?session_id=${sessionId || ''}`);
            allSchemes = await res.json();
            
            // Initial render
            renderSchemes(allSchemes);
            
        } catch (e) {
            console.error("Error fetching recommendations:", e);
        }
    };

    // Search Filter Logic
    const searchInput = document.getElementById('scheme-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const term = e.target.value.toLowerCase();
            const filtered = allSchemes.filter(s => 
                s.name.toLowerCase().includes(term) || 
                s.category.toLowerCase().includes(term) ||
                (s.target_group && s.target_group.toLowerCase().includes(term))
            );
            renderSchemes(filtered);
        });
    }

    // Call on load
    fetchRecommendations();
    
    // 6. Close Modal
    const modalEl = document.getElementById('newChatModal');
    if (modalEl) {
        const modal = bootstrap.Modal.getInstance(modalEl);
        if (modal) modal.hide();
    }

    // Store current profile globally
    let currentProfileData = {};

    // Helper to capture profile update from chat response
    const updateProfileGlobals = (profile) => {
        currentProfileData = profile;
    };

    const appendMessage = (role, content) => {
        // Hide Hero Section on first message
        const hero = document.getElementById('hero-section');
        if (hero) hero.style.display = 'none';

        const div = document.createElement('div');
        div.className = `d-flex w-100 mb-3 ${role === 'user' ? 'justify-content-end' : 'justify-content-start'}`;
        
        const bubble = document.createElement('div');
        bubble.className = `message-bubble ${role === 'user' ? 'message-user' : 'message-ai'}`;
        
        if (role === 'assistant') {
            bubble.innerHTML = marked.parse(content);
        } else {
            bubble.textContent = content;
        }

        div.appendChild(bubble);
        chatBox.appendChild(div);
        
        // Force all links in the new message to open in a new tab
        const links = bubble.querySelectorAll('a');
        links.forEach(link => {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        });

        scrollToBottom();
    };

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        // Add User Message
        appendMessage('user', message);
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

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, session_id: sessionId, language: currentLanguage })
            });

            const data = await response.json();
            
            // Remove typing indicator
            document.getElementById('typing').remove();

            if (data.error) {
                appendMessage('assistant', `Error: ${data.error}`);
            } else {
                appendMessage('assistant', data.response);
                
                // Update Session
                if (data.session_id) {
                    sessionId = data.session_id;
                    localStorage.setItem('chat_session_id', sessionId);
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
            appendMessage('assistant', 'Network Error. Is the backend running?');
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
        
        // Refresh recommendations (reset to default)
        fetchRecommendations();
    }
});
