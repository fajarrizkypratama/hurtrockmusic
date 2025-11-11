// === Domain Config injected from config.txt ===
const CHAT_DOMAIN = "chat.hurtrock-store.com";
const KASIR_DOMAIN = "www.hurtrock-store.com";
const MAIN_DOMAIN = "hurtrock-store.com";
// =================================================

/**
 * Floating Chat Widget - JavaScript Handler
 * Handles WebSocket connection, messaging, product tagging, and real-time chat
 */

class FloatingChat {
    constructor() {
        this.ws = null;
        this.chatToken = null;
        this.currentUser = null;
        this.isConnected = false;
        this.selectedProduct = null;
        this.typingTimer = null;
        this.unreadCount = 0;
        this.roomName = "";
        this.last_heartbeat = null; // Track last heartbeat time

        // Initialize chat when DOM is ready
        if (document.readyState === "loading") {
            document.addEventListener("DOMContentLoaded", () => this.init());
        } else {
            this.init();
        }
    }

    async init() {
        try {
            await this.getCurrentUser();
            
            // Hide chat for admin and staff (they have admin chat interface)
            if (
                this.currentUser &&
                (this.currentUser.role === "admin" || this.currentUser.role === "staff")
            ) {
                this.hideChatContainer();
                return;
            }
            
            // For buyer users: initialize full chat
            if (this.currentUser && this.currentUser.role === "buyer") {
                await this.getChatToken();
                this.setupEventListeners();
                this.generateRoomName();
                this.setupWebSocket();
                // Hide contact modal for logged in buyers
                const contactModal = document.getElementById('contact-us-modal');
                if (contactModal) contactModal.style.display = 'none';
            } else {
                // For guests (not logged in): show floating button with contact modal
                const chatWindow = document.getElementById('chat-window');
                if (chatWindow) chatWindow.style.display = 'none';
                // Contact modal will be shown when button is clicked
            }
        } catch (error) {
            console.error("Failed to initialize chat:", error);
            // Keep button visible for contact options
            const chatWindow = document.getElementById('chat-window');
            if (chatWindow) chatWindow.style.display = 'none';
        }
    }

    async getCurrentUser() {
        try {
            // Check if user is logged in by checking for user data in DOM first
            const userDataElement = document.querySelector("[data-user-id]");
            if (userDataElement) {
                this.currentUser = {
                    id: userDataElement.dataset.userId,
                    name: userDataElement.dataset.userName,
                    email: userDataElement.dataset.userEmail,
                    role: userDataElement.dataset.userRole,
                };
            } else {
                // No user data in DOM means user is not logged in (guest)
                // Don't make API call for guests - just leave currentUser null
                this.currentUser = null;
                console.log("Guest user detected, showing contact options");
                return;
            }

            // Hide chat for admin and staff users since they have admin chat interface
            if (
                this.currentUser &&
                (this.currentUser.role === "admin" ||
                    this.currentUser.role === "staff")
            ) {
                console.log("Admin/Staff user detected, hiding floating chat");
                this.hideChatContainer();
                return;
            }
        } catch (error) {
            console.error("Error getting current user:", error);
            // Don't hide container for error cases - let guest use contact modal
            this.currentUser = null;
        }
    }

    hideChatContainer() {
        const chatContainer = document.getElementById(
            "floating-chat-container",
        );
        if (chatContainer) {
            chatContainer.style.display = "none";
        }
    }

    getChatApiUrl() {
        // Auto-detect domain and use appropriate chat API endpoint
        const currentHost = window.location.hostname;
        const protocol = window.location.protocol;

        // For Replit deployment, always use same origin to avoid CORS
        if (
            currentHost.includes("replit.dev") ||
            currentHost.includes("repl.co")
        ) {
            return `${protocol}//${currentHost}/api/chat/token`;
        }

        // For custom domains (non-Replit), token endpoint is on main Flask app (port 5000), NOT Django service (port 8000)
        // So we use the current domain (main site), not chat subdomain
        if (
            !currentHost.includes("replit.dev") &&
            !currentHost.includes("repl.co") &&
            !currentHost.includes("localhost") &&
            !currentHost.includes("127.0.0.1")
        ) {
            // Token is on Flask app - use current domain (same origin)
            return `${protocol}//${currentHost}/api/chat/token`;
        }

        // For localhost development - Flask app on port 5000
        if (currentHost === "localhost" || currentHost === "127.0.0.1") {
            return "http://localhost:5000/api/chat/token";
        }

        // Default: use same origin (no port specification to avoid CORS)
        return `${protocol}//${currentHost}/api/chat/token`;
    }

    async getChatToken() {
        try {
            // Try primary URL first
            let chatApiUrl = this.getChatApiUrl();
            let response = await fetch(chatApiUrl, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "same-origin",
            });

            // If primary URL fails and we're not on tunnel domains, try fallback
            if (
                !response.ok &&
                !window.location.hostname.includes("hurtrock-store.com")
            ) {
                console.log("Primary chat API URL failed, trying fallback...");
                // Try with /chat path as fallback
                const fallbackUrl = `${window.location.protocol}//${window.location.hostname}/api/chat/token`;
                response = await fetch(fallbackUrl, {
                    method: "GET",
                    headers: {
                        "Content-Type": "application/json",
                    },
                    credentials: "same-origin",
                });

                if (response.ok) {
                    chatApiUrl = fallbackUrl;
                }
            }

            if (response.ok) {
                const data = await response.json();
                this.chatToken = data.token;
                this.currentUser = data.user;
                console.log(
                    "Chat token obtained successfully from:",
                    chatApiUrl,
                );
            } else {
                const errorText = await response.text();
                console.error(
                    "Chat token request failed:",
                    response.status,
                    errorText,
                );
                throw new Error(`Failed to get chat token: ${response.status}`);
            }
        } catch (error) {
            console.error("Error getting chat token:", error);
            // Try to show a more user-friendly message
            if (error.message.includes("Failed to fetch")) {
                console.error(
                    "Network error - chat service may not be available",
                );
            }
            throw error;
        }
    }

    generateRoomName() {
        // Create room name based on user role
        if (
            this.currentUser.role === "admin" ||
            this.currentUser.role === "staff"
        ) {
            this.roomName = "support_room";
        } else {
            this.roomName = `user_${this.currentUser.id}`;
        }
    }

    setupWebSocket() {
        if (!this.chatToken) {
            console.error("No chat token available");
            return;
        }

        // Use consistent room naming pattern: buyer_{user_id}
        const roomName = `buyer_${this.currentUser.id}`;
        this.roomName = roomName;

        const wsProtocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        let wsUrls = [];

        // Auto-detect domain for WebSocket connections
        const currentHost = window.location.hostname;

        // For Replit deployment, use same domain with port 8000
        if (currentHost.includes("replit.dev") || currentHost.includes("repl.co")) {
            // Replit: Django chat service runs on same domain with port 8000
            wsUrls.push(`${wsProtocol}//${currentHost}:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
            // Fallback without port if proxy exists
            wsUrls.push(`${wsProtocol}//${currentHost}/ws/chat/${roomName}/?token=${this.chatToken}`);
        } else if (currentHost === "localhost" || currentHost === "127.0.0.1") {
            // Local development - try multiple localhost variants
            wsUrls.push(`ws://127.0.0.1:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
            wsUrls.push(`ws://localhost:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
            wsUrls.push(`ws://0.0.0.0:8000/ws/chat/${roomName}/?token=${this.chatToken}`);
        } else {
            // For hurtrock-store.com and other custom domains with Cloudflare tunnel
            // Use the tunnel routing - WebSocket traffic goes to same domain but routed by path
            wsUrls.push(`${wsProtocol}//${currentHost}/ws/chat/${roomName}/?token=${this.chatToken}`);
            
            // Try www variant if not already
            if (!currentHost.startsWith("www.") && currentHost.includes("hurtrock-store.com")) {
                wsUrls.push(`${wsProtocol}//www.hurtrock-store.com/ws/chat/${roomName}/?token=${this.chatToken}`);
            }
        }

        console.log("Buyer attempting WebSocket connection with URLs:", wsUrls);
        this.updateConnectionStatus("connecting");

        this.tryConnectWithFallback(wsUrls, 0);
    }

    tryConnectWithFallback(urls, urlIndex) {
        if (urlIndex >= urls.length) {
            console.error("All WebSocket URLs failed");
            this.updateConnectionStatus("error");
            this.displaySystemMessage(
                "Tidak dapat terhubung ke server chat. Silakan refresh halaman.",
                "error",
            );
            return;
        }

        const wsUrl = urls[urlIndex];
        console.log(
            `Trying WebSocket URL ${urlIndex + 1}/${urls.length}:`,
            wsUrl,
        );

        try {
            this.ws = new WebSocket(wsUrl);
            this.reconnectAttempts = 0;
            this.maxReconnectAttempts = 10;
            this.reconnectDelay = 1000;
            this.heartbeatInterval = null;

            this.ws.onopen = (event) => {
                console.log("WebSocket connected successfully to:", wsUrl);
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.reconnectDelay = 1000; // Reset delay
                this.updateConnectionStatus("connected");
                this.startHeartbeat();
                this.loadChatHistory(); // Load history upon connection
            };

            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error("Error parsing WebSocket message:", error);
                }
            };

            this.ws.onclose = (event) => {
                console.log("WebSocket closed:", event.code, event.reason);
                this.isConnected = false;
                this.stopHeartbeat();

                if (event.code !== 1000 && event.code !== 1001) {
                    // Connection lost unexpectedly - try next URL
                    console.log("Connection failed, trying next URL...");
                    setTimeout(() => {
                        this.tryConnectWithFallback(urls, urlIndex + 1);
                    }, 1000);
                } else {
                    // Normal close
                    this.updateConnectionStatus("disconnected");
                }
            };

            this.ws.onerror = (error) => {
                console.error('WebSocket error for URL:', wsUrl, error);
                console.log('WebSocket readyState:', this.ws.readyState);
                console.log('Error event details:', {
                    type: error.type,
                    target: error.target,
                    currentTarget: error.currentTarget
                });
                // Don't change status here, let onclose handle it
                this.isConnected = false;
            };
        } catch (error) {
            console.error("Error creating WebSocket for URL:", wsUrl, error);
            // Try next URL immediately
            setTimeout(() => {
                this.tryConnectWithFallback(urls, urlIndex + 1);
            }, 500);
        }
    }

    attemptReconnect() {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error("Max reconnection attempts reached");
            this.updateConnectionStatus("error");
            this.displaySystemMessage(
                "Koneksi chat gagal. Silakan refresh halaman.",
                "error",
            );
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(
            this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
            30000,
        ); // Max 30 seconds

        console.log(
            `Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts}) in ${delay}ms`,
        );
        this.updateConnectionStatus("connecting");

        setTimeout(() => {
            if (!this.isConnected) {
                this.setupWebSocket();
            }
        }, delay);
    }

    startHeartbeat() {
        this.stopHeartbeat(); // Clear any existing heartbeat
        this.heartbeatInterval = setInterval(() => {
            if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(
                    JSON.stringify({
                        type: "heartbeat",
                        timestamp: new Date().toISOString(),
                    }),
                );
                this.last_heartbeat = new Date(); // Record send time
            }
        }, 30000); // Send heartbeat every 30 seconds
    }

    stopHeartbeat() {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
    }

    handleWebSocketMessage(data) {
        console.log("Buyer received WebSocket message:", data);

        switch (data.type) {
            case 'chat_message':
                // Handle incoming chat message
                if (data.message) {
                    this.displayMessage(data.message);
                }
                break;

            case 'connection_established':
                // Handle connection established
                console.log('Connection established:', data);
                break;

            case 'typing_status':
            case 'typing_indicator':
                // Handle typing indicator from other users
                if (data.user_id != this.currentUser.id) {
                    this.updateTypingIndicator(data);
                }
                break;

            case 'heartbeat':
                // Handle heartbeat from server
                console.debug('Heartbeat received from server:', data);
                // Respond with heartbeat acknowledgment
                if (this.isConnected && this.ws.readyState === WebSocket.OPEN) {
                    this.ws.send(JSON.stringify({
                        type: 'heartbeat_ack',
                        timestamp: data.timestamp
                    }));
                }
                break;

            case 'heartbeat_ack':
                // Handle heartbeat acknowledgment
                console.debug('Heartbeat acknowledged:', data);
                this.last_heartbeat = new Date();
                break;

            case 'error':
                console.error('Chat error:', data.message);
                this.displaySystemMessage(
                    data.message || 'Terjadi kesalahan',
                    'error',
                );
                break;

            default:
                console.log('Unknown message type:', data.type || 'undefined type');
        }
    }

    isChatMinimized() {
        const chatWindow = document.getElementById("chat-window");
        return chatWindow.style.display === "none";
    }

    handleNotification(notification) {
        switch (notification.type) {
            case "message_read":
                // Remove unread indicator if exists
                this.handleMessageRead(notification.message_id);
                break;
            case "new_message":
                if (this.isChatMinimized()) {
                    this.showNotification(
                        notification.title,
                        notification.body,
                    );
                    this.incrementUnreadCount();
                }
                break;
        }
    }

    handleMessageRead(messageId) {
        // Mark message as read in UI
        const messageElement = document.querySelector(
            `[data-message-id="${messageId}"]`,
        );
        if (messageElement) {
            const readIndicator =
                messageElement.querySelector(".read-indicator");
            if (readIndicator) {
                readIndicator.classList.add("read");
                readIndicator.innerHTML =
                    '<i class="fas fa-check-double text-primary"></i>';
            }
        }
    }

    updateConnectionStatus(status) {
        const statusElement = document.getElementById("connection-status");
        if (statusElement) {
            statusElement.className = `connection-status ${status}`;
            switch (status) {
                case "connected":
                    statusElement.textContent = "Terhubung";
                    break;
                case "connecting":
                    statusElement.textContent = "Menghubungkan...";
                    break;
                case "disconnected":
                    statusElement.textContent =
                        "Terputus - mencoba menyambung kembali...";
                    break;
                case "error":
                    statusElement.textContent = "Koneksi bermasalah";
                    break;
            }
        }
    }

    setupEventListeners() {
        // Chat message input
        const messageInput = document.getElementById("chat-message-input");
        if (messageInput) {
            messageInput.addEventListener("keypress", (e) =>
                this.handleChatKeyPress(e),
            );
            messageInput.addEventListener("input", () => this.handleTyping());
        }

        // Send button
        const sendBtn = document.getElementById("send-message-btn");
        if (sendBtn) {
            sendBtn.addEventListener("click", () => this.sendChatMessage());
        }

        // Media upload button - ensure it's properly connected
        const mediaBtn = document.getElementById("media-upload-btn");
        if (mediaBtn) {
            mediaBtn.addEventListener("click", (e) => {
                e.preventDefault();
                this.showMediaUpload();
            });
        }

        // Media file input - ensure it's properly connected
        const mediaInput = document.getElementById("media-file-input");
        if (mediaInput) {
            mediaInput.addEventListener("change", (e) => {
                if (e.target.files && e.target.files.length > 0) {
                    this.handleMediaUpload(e);
                }
            });
        }

        // Product search
        const productSearch = document.getElementById("product-search");
        if (productSearch) {
            productSearch.addEventListener("keyup", () =>
                this.searchProducts(),
            );
        }
    }

    handleChatKeyPress(event) {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            this.sendChatMessage();
        }
    }

    sendChatMessage() {
        const messageInput = document.getElementById("chat-message-input");
        const message = messageInput.value.trim();

        if (!message) return;

        if (!this.isConnected) {
            this.displaySystemMessage(
                "Chat tidak terhubung. Mencoba menyambung kembali...",
                "warning",
            );
            this.setupWebSocket();
            return;
        }

        const messageData = {
            type: "chat_message",
            message: message,
            product_id: this.selectedProduct ? this.selectedProduct.id : null,
        };

        this.ws.send(JSON.stringify(messageData));
        messageInput.value = "";

        // Clear product tag after sending
        if (this.selectedProduct) {
            this.clearProductTag();
        }
    }

    handleTyping() {
        if (!this.isConnected) return;

        // Send typing start indicator
        this.ws.send(
            JSON.stringify({
                type: "typing_indicator",
                is_typing: true,
            }),
        );

        // Clear existing timer
        if (this.typingTimer) {
            clearTimeout(this.typingTimer);
        }

        // Send typing stop indicator after 2 seconds
        this.typingTimer = setTimeout(() => {
            if (this.isConnected) {
                this.ws.send(
                    JSON.stringify({
                        type: "typing_indicator",
                        is_typing: false,
                    }),
                );
            }
        }, 2000);
    }

    displayMessage(data) {
        const messagesContainer = document.getElementById("chat-messages");
        if (!messagesContainer) return;

        // DEBUG: Log received message data
        console.log('[BUYER CHAT] Message data:', data);
        if (data.media_data) console.log('[BUYER CHAT] media_data:', data.media_data);
        if (data.media_url) console.log('[BUYER CHAT] media_url:', data.media_url);

        const welcomeMsg = messagesContainer.querySelector(".chat-welcome-msg");

        // Remove welcome message when first message arrives
        if (welcomeMsg) {
            welcomeMsg.remove();
        }

        const messageDiv = document.createElement("div");
        const isSent = data.user_id == this.currentUser.id;
        messageDiv.className = `chat-message ${isSent ? "sent" : "received"}`;

        let productTagHtml = "";
        // Check for product info first, then fallback to product_id
        if (data.product_info) {
            const productName = this.escapeHtml(
                data.product_info.name || "Unknown Product",
            );
            const productPrice = data.product_info.price
                ? this.formatPrice(data.product_info.price)
                : "N/A";
            const productImage =
                data.product_info.image_url || "/static/images/placeholder.jpg";
            const productUrl = data.product_info.url || `/produk/${data.product_info.slug}` || `/produk/id/${data.product_info.id}`;

            productTagHtml = `
                <div class="product-tag" data-product-url="${productUrl}" style="cursor: pointer;">
                    <img src="${productImage}" alt="${productName}" onerror="this.src='/static/images/placeholder.jpg'">
                    <div class="product-tag-info">
                        <h6>${productName}</h6>
                        <p>Rp ${productPrice}</p>
                        <small>Klik untuk lihat detail</small>
                    </div>
                </div>
            `;
        } else if (data.product_id) {
            // Create placeholder and try to fetch product info
            const fallbackUrl = `/produk/id/${data.product_id}`;
            productTagHtml = `
                <div class="product-tag loading" data-product-url="${fallbackUrl}" data-product-id="${data.product_id}" style="cursor: pointer;">
                    <img src="/static/images/placeholder.jpg" alt="Loading..." onerror="this.src='/static/images/placeholder.jpg'">
                    <div class="product-tag-info">
                        <h6>Memuat produk...</h6>
                        <p>Klik untuk lihat detail</p>
                    </div>
                </div>
            `;

            // Fetch product info asynchronously
            this.fetchProductInfo(data.product_id)
                .then((productInfo) => {
                    if (productInfo && messageDiv) {
                        this.updateProductTagDisplay(messageDiv, productInfo);
                    }
                })
                .catch((error) => {
                    console.error("Failed to fetch product info:", error);
                    // Keep the fallback display
                });
        }

        const timestamp =
            data.timestamp || data.created_at || new Date().toISOString();
        const timeFormatted = this.formatTime(timestamp);

        // Media HTML if present - handle both nested media_data and direct media fields
        let mediaHtml = "";
        let mediaUrl = null;
        let mediaType = null;
        let mediaFilename = "";

        console.log('[BUYER CHAT] Processing media data:', data);
        console.log('[BUYER CHAT] Full message object:', JSON.stringify(data, null, 2));

        // Check for media_data object first (sent format)
        if (data.media_data && data.media_data.media_url) {
            mediaUrl = data.media_data.media_url;
            mediaType = data.media_data.media_type;
            mediaFilename = data.media_data.media_filename || data.media_data.filename || '';
            console.log('[BUYER CHAT] Using media_data:', { mediaUrl, mediaType, mediaFilename });
        }
        // Fallback to direct fields (some backend formats)
        else if (data.media_url && data.media_type) {
            mediaUrl = data.media_url;
            mediaType = data.media_type;
            mediaFilename = data.media_filename || '';
            console.log('[BUYER CHAT] Using direct media fields:', { mediaUrl, mediaType, mediaFilename });
        }

        if (mediaUrl && mediaType) {
            console.log('[BUYER CHAT] Generating media HTML for:', mediaUrl);

            // Ensure URL is absolute and accessible
            let fullMediaUrl = mediaUrl;
            if (!mediaUrl.startsWith('http') && !mediaUrl.startsWith('/')) {
                fullMediaUrl = `/uploads/medias_sends/${mediaUrl}`;
            }

            const escapedUrl = this.escapeHtml(fullMediaUrl);
            const escapedFilename = this.escapeHtml(mediaFilename || 'Media file');

            if (mediaType === "image" || mediaType.startsWith("image/")) {
                mediaHtml = `
                    <div class="message-media chat-media-container" style="margin: 6px 0; max-width: 250px;">
                        <div class="media-wrapper" style="position: relative; border-radius: 12px; overflow: hidden; background: #f8f9fa; box-shadow: 0 1px 4px rgba(0,0,0,0.1);">
                            <img src="${escapedUrl}" alt="${escapedFilename}" class="chat-media-image"
                                 onclick="window.open('${escapedUrl}', '_blank')"
                                 onload="this.style.opacity='1'; this.parentNode.style.background='transparent';"
                                 onerror="this.parentNode.innerHTML='<div style=\\'padding: 16px; text-align: center; color: #e74c3c; background: #fdf2f2; border-radius: 12px;\\'>📷 Gambar tidak dapat dimuat<br><small style=\\'font-size: 10px; margin-top: 4px; display: block;\\'>${escapedFilename}</small></div>';"
                                 style="width: 100%; height: auto; max-height: 200px; object-fit: cover; display: block; cursor: pointer; opacity: 0; transition: opacity 0.3s ease;">
                        </div>
                        <div class="media-info" style="font-size: 9px; color: ${isSent ? 'rgba(255,255,255,0.7)' : '#6c757d'}; margin-top: 3px; text-align: ${isSent ? 'right' : 'left'}; padding: 0 2px;">
                            📷 ${escapedFilename || 'Gambar'}
                        </div>
                    </div>
                `;
                console.log('[BUYER CHAT] ✅ Generated WhatsApp-style image HTML');
            } else if (mediaType === "video" || mediaType.startsWith("video/")) {
                mediaHtml = `
                    <div class="message-media chat-media-container" style="margin: 6px 0; max-width: 250px;">
                        <div class="media-wrapper" style="position: relative; border-radius: 12px; overflow: hidden; background: #000; box-shadow: 0 1px 4px rgba(0,0,0,0.1);">
                            <video controls class="chat-media-video" preload="metadata"
                                   onloadeddata="console.log('✅ Video loaded successfully:', '${escapedUrl}');"
                                   onerror="this.parentNode.innerHTML='<div style=\\'padding: 16px; text-align: center; color: #e74c3c; background: #fdf2f2; border-radius: 12px;\\'>🎥 Video tidak dapat dimuat<br><small style=\\'font-size: 10px; margin-top: 4px; display: block;\\'>${escapedFilename}</small></div>';"
                                   style="width: 100%; height: auto; max-height: 200px; display: block; border-radius: 12px;">
                                <source src="${escapedUrl}" type="${mediaType}">
                                Browser Anda tidak mendukung video.
                            </video>
                        </div>
                        <div class="media-info" style="font-size: 9px; color: ${isSent ? 'rgba(255,255,255,0.7)' : '#6c757d'}; margin-top: 3px; text-align: ${isSent ? 'right' : 'left'}; padding: 0 2px;">
                            🎥 ${escapedFilename || 'Video'}
                        </div>
                    </div>
                `;
                console.log('[BUYER CHAT] ✅ Generated WhatsApp-style video HTML');
            } else {
                console.log('[BUYER CHAT] ⚠️ Unknown media type:', mediaType);
                mediaHtml = `
                    <div class="message-media chat-media-container" style="margin: 6px 0; max-width: 250px;">
                        <div class="media-wrapper" style="padding: 12px; background: #f8f9fa; border-radius: 12px; text-align: center; border: 1px solid #e9ecef;">
                            <div style="font-size: 20px; margin-bottom: 6px;">📎</div>
                            <div style="font-size: 11px; color: #495057; font-weight: 500;">${escapedFilename || 'File attachment'}</div>
                            <div style="font-size: 9px; color: #6c757d; margin-top: 3px;">Type: ${mediaType}</div>
                        </div>
                    </div>
                `;
            }
        } else {
            console.log('[BUYER CHAT] ⚠️ No media data found in message - checking for missing fields...');
            if (!data.media_url && !data.media_data) {
                console.log('[BUYER CHAT] ❌ No media_url or media_data fields present');
            }
        }

        messageDiv.innerHTML = `
            <div class="message-content">
                ${data.message ? this.escapeHtml(data.message) : ""}
                ${mediaHtml}
                ${productTagHtml}
                <div class="message-meta">
                    <strong>${this.escapeHtml(data.user_name || "User")}</strong> • ${timeFormatted}
                </div>
            </div>
        `;

        messagesContainer.appendChild(messageDiv);

        // Add click event listener to product tags after they're added to DOM
        const productTags = messageDiv.querySelectorAll(
            ".product-tag[data-product-url]",
        );
        productTags.forEach((tag) => {
            tag.addEventListener("click", function (e) {
                e.preventDefault();
                const productUrl = this.getAttribute("data-product-url");
                window.open(productUrl, "_blank");
            });
        });

        // Smooth scroll to bottom with proper timing
        setTimeout(() => {
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: "smooth",
            });
        }, 100);
    }

    async fetchProductInfo(productId) {
        try {
            const response = await fetch(`/api/products/${productId}`);
            if (response.ok) {
                return await response.json();
            }
            return null;
        } catch (error) {
            console.error("Error fetching product info:", error);
            return null;
        }
    }

    updateProductTagDisplay(messageDiv, productInfo) {
        const productTag = messageDiv.querySelector(
            ".product-tag[data-product-id]",
        );
        if (productTag && productInfo) {
            const productName = this.escapeHtml(
                productInfo.name || "Unknown Product",
            );
            const productPrice = productInfo.price
                ? this.formatPrice(productInfo.price)
                : "N/A";
            const productImage =
                productInfo.image_url || "/static/images/placeholder.jpg";
            const productUrl = productInfo.url || `/produk/${productInfo.slug}` || `/produk/id/${productInfo.id}`;

            productTag.classList.remove("loading");
            productTag.setAttribute("data-product-url", productUrl);

            productTag.innerHTML = `
                <img src="${productImage}" alt="${productName}" onerror="this.src='/static/images/placeholder.jpg'">
                <div class="product-tag-info">
                    <h6>${productName}</h6>
                    <p>Rp ${productPrice}</p>
                    <small>Klik untuk lihat detail</small>
                </div>
            `;

            // Re-add click event listener
            productTag.addEventListener("click", function (e) {
                e.preventDefault();
                window.open(productUrl, "_blank");
            });
        }
    }

    displaySystemMessage(message, type = "info") {
        const messagesContainer = document.getElementById("chat-messages");
        const messageDiv = document.createElement("div");
        messageDiv.className = `chat-message system ${type}`;
        messageDiv.innerHTML = `
            <div class="message-content system-message">
                <i class="fas fa-info-circle"></i>
                ${this.escapeHtml(message)}
            </div>
        `;
        messagesContainer.appendChild(messageDiv);

        // Smooth scroll to bottom with proper timing
        setTimeout(() => {
            messagesContainer.scrollTo({
                top: messagesContainer.scrollHeight,
                behavior: "smooth",
            });
        }, 100);
    }

    updateTypingIndicator(data) {
        const typingIndicator = document.getElementById("typing-indicator");
        const typingUserSpan = typingIndicator ? typingIndicator.querySelector(".typing-user") : null;
        if (!typingIndicator || !typingUserSpan) return;

        console.log('[BUYER CHAT] Typing indicator data:', data);
        console.log('[BUYER CHAT] Current user:', this.currentUser);

        // Check if the typing event is from someone else and if they are typing
        if (data.is_typing && data.user_name && data.user_name !== this.currentUser.name && data.user_id != this.currentUser.id) {
            typingUserSpan.textContent = data.user_name;
            typingIndicator.style.display = "flex";
            console.log('[BUYER CHAT] Showing typing indicator for:', data.user_name);
        } else {
            typingIndicator.style.display = "none";
            console.log('[BUYER CHAT] Hiding typing indicator');
        }
    }

    incrementUnreadCount() {
        this.unreadCount++;
        this.updateChatBadge();

        // If chat is minimized, show notification
        const chatWindow = document.getElementById("chat-window");
        if (chatWindow.style.display === "none") {
            this.showNotification("Pesan baru dari customer service");
        }
    }

    updateChatBadge() {
        const badge = document.getElementById("chat-badge");
        if (this.unreadCount > 0) {
            badge.textContent =
                this.unreadCount > 99 ? "99+" : this.unreadCount;
            badge.style.display = "block";
        } else {
            badge.style.display = "none";
        }
    }

    showNotification(
        title = "Pesan chat baru",
        body = "Anda mendapat pesan baru dari customer service.",
    ) {
        // Simple browser notification (if permission granted)
        if (Notification.permission === "granted") {
            new Notification(title, {
                body: body,
                icon: "/static/images/favicon.ico",
            });
        } else if (Notification.permission === "default") {
            Notification.requestPermission().then((permission) => {
                if (permission === "granted") {
                    new Notification(title, {
                        body: body,
                        icon: "/static/images/favicon.ico",
                    });
                }
            });
        }
    }

    async loadChatHistory() {
        try {
            const roomName = `buyer_${this.currentUser.id}`;

            // Always try Flask proxy first (same origin), then Django directly
            const endpoints = [
                `/api/rooms/${roomName}/messages/`, // Flask proxy (recommended)
            ];

            let lastError = null;

            for (const endpoint of endpoints) {
                try {
                    console.log(`[FLOATING CHAT] Loading history from: ${endpoint}`);
                    
                    const response = await fetch(endpoint, {
                        headers: {
                            Authorization: `Bearer ${this.chatToken}`,
                            "Content-Type": "application/json",
                            "Accept": "application/json"
                        },
                        credentials: 'same-origin'
                    });

                    if (response.ok) {
                        const data = await response.json();
                        console.log("Chat history loaded successfully:", data);

                        // Handle different response formats
                        let messages = [];
                        if (data.results && Array.isArray(data.results)) {
                            messages = data.results;
                        } else if (Array.isArray(data)) {
                            messages = data;
                        } else if (data.messages && Array.isArray(data.messages)) {
                            messages = data.messages;
                        }

                        if (messages.length > 0) {
                            console.log(`Loading ${messages.length} messages`);
                            messages.forEach((message) => {
                                if (message && typeof message === "object") {
                                    this.displayMessage(message);
                                }
                            });
                            
                            // Scroll to bottom after loading history
                            setTimeout(() => {
                                const messagesContainer = document.getElementById("chat-messages");
                                if (messagesContainer) {
                                    messagesContainer.scrollTo({
                                        top: messagesContainer.scrollHeight,
                                        behavior: "smooth",
                                    });
                                }
                            }, 100);
                            return; // Success, exit the loop
                        } else {
                            console.log("No messages found, but request was successful");
                            return; // Empty but successful
                        }
                    } else {
                        const errorText = await response.text();
                        lastError = `HTTP ${response.status} from ${endpoint}: ${errorText}`;
                        console.error(`Failed to load chat history from ${endpoint}:`, response.status, errorText);
                        continue;
                    }
                } catch (error) {
                    lastError = `${error.message} from ${endpoint}`;
                    console.error(`Error loading chat history from ${endpoint}:`, error);
                    continue;
                }
            }

            console.error("Failed to load chat history from all endpoints. Last error:", lastError);
            this.displaySystemMessage(
                "Tidak dapat memuat riwayat chat. Silakan refresh halaman.",
                "warning",
            );
        } catch (error) {
            console.error("Unexpected error during chat history loading:", error);
            this.displaySystemMessage(
                "Terjadi kesalahan saat memuat riwayat chat.",
                "error",
            );
        }
    }

    async searchProducts() {
        const searchInput = document.getElementById("product-search");
        const query = searchInput.value.trim();

        if (query.length < 2) {
            document.getElementById("products-list").innerHTML = "";
            return;
        }

        try {
            const response = await fetch(
                `/search?q=${encodeURIComponent(query)}`,
            );
            if (response.ok) {
                const products = await response.json();
                this.displayProductResults(products);
            }
        } catch (error) {
            console.error("Error searching products:", error);
        }
    }

    displayProductResults(products) {
        const productsList = document.getElementById("products-list");

        if (products.length === 0) {
            productsList.innerHTML =
                '<p class="text-muted">Tidak ada produk ditemukan.</p>';
            return;
        }

        productsList.innerHTML = products
            .map(
                (product) => `
            <div class="product-item" onclick="floatingChat.selectProduct(${product.id}, '${this.escapeHtml(product.name)}', '${product.price}', '${product.image_url}')">
                <img src="${product.image_url || "/static/images/placeholder.jpg"}" alt="${this.escapeHtml(product.name)}">
                <div class="product-item-info">
                    <h6>${this.escapeHtml(product.name)}</h6>
                    <p class="product-item-price">Rp ${this.formatPrice(product.price)}</p>
                    <p>${this.escapeHtml(product.brand || "")}</p>
                </div>
            </div>
        `,
            )
            .join("");
    }

    selectProduct(id, name, price, imageUrl) {
        this.selectedProduct = { id, name, price, imageUrl };

        // If we have pending media, send it with the selected product
        if (this.pendingMediaData) {
            this.sendMediaMessage(
                this.pendingMediaData,
                this.pendingMediaData.caption,
            );
            // Close modal
            const modalElement = document.getElementById(
                "product-selector-modal",
            );
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();
            // Clean up pending data
            this.pendingMediaData = null;
        } else {
            // Normal product tagging
            this.showProductTagPreview();
            // Close modal
            const modalElement = document.getElementById(
                "product-selector-modal",
            );
            const modal = bootstrap.Modal.getInstance(modalElement);
            if (modal) modal.hide();
        }
    }

    showProductTagPreview() {
        const preview = document.getElementById("product-tag-preview");
        const image = document.getElementById("tagged-product-image");
        const name = document.getElementById("tagged-product-name");
        const price = document.getElementById("tagged-product-price");

        if (this.selectedProduct) {
            image.src =
                this.selectedProduct.imageUrl ||
                "/static/images/placeholder.jpg";
            name.textContent = this.selectedProduct.name;
            price.textContent = `Rp ${this.formatPrice(this.selectedProduct.price)}`;
            preview.style.display = "block";
        }
    }

    clearProductTag() {
        this.selectedProduct = null;
        const preview = document.getElementById("product-tag-preview");
        preview.style.display = "none";
    }

    formatPrice(price) {
        // Ensure price is a number before formatting
        const numericPrice = parseFloat(price);
        if (isNaN(numericPrice)) {
            return "N/A";
        }
        return new Intl.NumberFormat("id-ID", {
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(numericPrice);
    }

    formatTime(timestamp) {
        try {
            let date;

            if (!timestamp) {
                date = new Date();
            } else if (typeof timestamp === "string") {
                // Handle ISO strings, timestamp with timezone, and other formats
                if (timestamp.includes("T") || timestamp.includes("-")) {
                    // ISO format or date string - parse directly
                    date = new Date(timestamp);
                } else if (!isNaN(timestamp)) {
                    // Unix timestamp string
                    date = new Date(
                        parseInt(timestamp) *
                            (timestamp.length === 10 ? 1000 : 1),
                    );
                } else {
                    // Try direct parsing
                    date = new Date(timestamp);
                }
            } else if (typeof timestamp === "number") {
                // Unix timestamp - check if seconds or milliseconds
                date = new Date(
                    timestamp * (timestamp.toString().length === 10 ? 1000 : 1),
                );
            } else {
                date = new Date(timestamp);
            }

            // Validate the date
            if (!date || isNaN(date.getTime()) || date.getTime() === 0) {
                console.warn(
                    "Invalid timestamp, using current time:",
                    timestamp,
                );
                date = new Date();
            }

            // Ensure we have a reasonable date (not too far in past/future)
            const now = new Date();
            const diffYears = Math.abs(now.getFullYear() - date.getFullYear());
            if (diffYears > 10) {
                console.warn(
                    "Timestamp too far from current time, using current time:",
                    timestamp,
                );
                date = new Date();
            }

            // Format dengan timezone WIB (Asia/Jakarta) - Bandung, Indonesia
            return date.toLocaleTimeString("id-ID", {
                hour: "2-digit",
                minute: "2-digit",
                timeZone: "Asia/Jakarta",
            });
        } catch (error) {
            console.error(
                "Error formatting time:",
                error,
                "timestamp:",
                timestamp,
            );
            return new Date().toLocaleTimeString("id-ID", {
                hour: "2-digit",
                minute: "2-digit",
                timeZone: "Asia/Jakarta",
            });
        }
    }

    // === Media Upload & Handling ===
    showMediaUpload = () => {
        const input = document.createElement("input");
        input.type = "file";
        input.accept = "image/*,video/*";
        input.onchange = (event) => this.handleMediaUpload(event);
        input.click();
    };

    handleMediaUpload = (event) => {
        const file = event.target.files[0];
        if (!file) return;

        // Validasi ukuran (maks 10MB)
        if (file.size > 10 * 1024 * 1024) {
            alert("File terlalu besar (maks 10MB).");
            return;
        }

        // Validasi tipe file
        if (
            !file.type.startsWith("image/") &&
            !file.type.startsWith("video/")
        ) {
            alert("Format file tidak didukung. Pilih gambar atau video.");
            return;
        }

        this.pendingMediaFile = file;
        this.showMediaConfirmationModal(file);
    };

    showMediaConfirmationModal = (file) => {
        this.pendingMediaFile = file;

        // Buat modal jika belum ada
        let modalEl = document.getElementById("media-confirmation-modal");
        if (!modalEl) {
            modalEl = document.createElement("div");
            modalEl.id = "media-confirmation-modal";
            modalEl.className = "modal fade";
            modalEl.tabIndex = -1;
            modalEl.innerHTML = `
                <div class="modal-dialog modal-dialog-centered">
                  <div class="modal-content">
                    <div class="modal-header">
                      <h5 class="modal-title">Konfirmasi Upload</h5>
                      <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                      <img id="media-preview-img" src="" class="img-fluid mb-3 d-none" alt="Preview">
                      <video id="media-preview-video" class="img-fluid mb-3 d-none" controls></video>
                      <input id="media-caption-input" type="text" class="form-control" placeholder="Tambahkan caption (opsional)">
                    </div>
                    <div class="modal-footer">
                      <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Batal</button>
                      <button type="button" class="btn btn-primary" id="sendMediaBtn">Kirim</button>
                    </div>
                  </div>
                </div>
            `;
            document.body.appendChild(modalEl);
        }

        // Set preview
        const previewImg = modalEl.querySelector("#media-preview-img");
        const previewVideo = modalEl.querySelector("#media-preview-video");
        const url = URL.createObjectURL(file);

        if (file.type.startsWith("image/")) {
            previewImg.src = url;
            previewImg.classList.remove("d-none");
            previewVideo.classList.add("d-none");
        } else if (file.type.startsWith("video/")) {
            previewVideo.src = url;
            previewVideo.classList.remove("d-none");
            previewImg.classList.add("d-none");
        }

        // Pasang tombol kirim
        const sendBtn = modalEl.querySelector("#sendMediaBtn");
        sendBtn.onclick = () => this.uploadAndSendMedia();

        // Tampilkan modal
        const modal = new bootstrap.Modal(modalEl);
        modal.show();
    };

    closeMediaConfirmationModal = () => {
        const modalEl = document.getElementById("media-confirmation-modal");
        if (modalEl) {
            const modal = bootstrap.Modal.getInstance(modalEl);
            if (modal) modal.hide();
        }
    };

    uploadAndSendMedia = async () => {
        if (!this.pendingMediaFile) {
            console.error("No pending media file found.");
            alert(
                "Tidak ada file yang dipilih. Silakan pilih file terlebih dahulu.",
            );
            return;
        }

        if (!this.pendingMediaFile.name) {
            console.error("Pending media file has no name property.");
            alert("File tidak valid. Silakan pilih file lagi.");
            return;
        }

        const caption =
            document.getElementById("media-caption-input")?.value.trim() || "";

        try {
            this.closeMediaConfirmationModal();
            this.showUploadProgress();

            // Consistent file naming with server-side logic
            const originalName = this.pendingMediaFile.name;
            const fileExtension = originalName
                .substring(originalName.lastIndexOf("."))
                .toLowerCase();
            const timestamp = new Date()
                .toISOString()
                .replace(/[:.]/g, "-")
                .substring(0, 19);
            const userRole = 'buyer'; // Floating chat is always buyer
            const newFileName = `chat_${userRole}_${timestamp}_${this.currentUser.id}${fileExtension}`;

            const renamedFile = new File([this.pendingMediaFile], newFileName, {
                type: this.pendingMediaFile.type,
                lastModified: this.pendingMediaFile.lastModified,
            });

            const formData = new FormData();
            formData.append("file", renamedFile);

            // CSRF token
            let csrfToken = null;
            const csrfMeta = document.querySelector("meta[name='csrf-token']");
            if (csrfMeta) csrfToken = csrfMeta.getAttribute("content");

            const headers = {};
            if (csrfToken) headers["X-CSRFToken"] = csrfToken;

            const response = await fetch("/api/chat/upload-media", {
                method: "POST",
                headers: headers,
                body: formData,
                credentials: "same-origin",
            });

            if (response.ok) {
                const result = await response.json();
                this.hideUploadProgress();
                this.sendMediaMessage(result, caption);
            } else {
                let errorMessage = "Upload failed";
                try {
                    const errorData = await response.json();
                    errorMessage =
                        errorData.error || `Upload failed (${response.status})`;
                } catch {
                    if (response.status === 400) {
                        errorMessage =
                            "Format file tidak didukung atau ukuran terlalu besar (maksimal 10MB)";
                    } else if (response.status === 500) {
                        errorMessage =
                            "Server error - masalah direktori upload";
                    } else {
                        errorMessage = `Server error (${response.status}). Silakan coba lagi.`;
                    }
                }
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error("Media upload error:", error);
            this.hideUploadProgress();
            alert("Gagal upload media: " + error.message);
        } finally {
            this.pendingMediaFile = null;
        }
    };

    async uploadWithProductTag(previewUrl) {
        if (!this.pendingMediaFile) {
            console.error(
                "No pending media file found for product tag upload.",
            );
            alert(
                "Tidak ada file yang dipilih. Silakan pilih file terlebih dahulu.",
            );
            return;
        }

        if (!this.pendingMediaFile.name) {
            console.error("Pending media file has no name property.");
            alert("File tidak valid. Silakan pilih file lagi.");
            return;
        }

        const caption =
            document.getElementById("media-caption-input")?.value.trim() || "";

        try {
            // Upload media first
            this.closeMediaConfirmationModal();
            this.showUploadProgress();

            // Create auto-renamed file with timestamp
            const originalName = this.pendingMediaFile.name;
            const fileExtension = originalName
                .substring(originalName.lastIndexOf("."))
                .toLowerCase();
            const timestamp = new Date()
                .toISOString()
                .replace(/[:.]/g, "-")
                .substring(0, 19);
            const newFileName = `chat_media_${timestamp}${fileExtension}`;

            // Create new File object with auto-renamed filename
            const renamedFile = new File([this.pendingMediaFile], newFileName, {
                type: this.pendingMediaFile.type,
                lastModified: this.pendingMediaFile.lastModified,
            });

            const formData = new FormData();
            formData.append("file", renamedFile);

            // Get CSRF token
            let csrfToken = null;
            const csrfMeta = document.querySelector('meta[name="csrf-token"]');
            if (csrfMeta) {
                csrfToken = csrfMeta.getAttribute("content");
            }

            const headers = {};
            if (csrfToken) {
                headers["X-CSRFToken"] = csrfToken;
            }

            const response = await fetch("/api/chat/upload-media", {
                method: "POST",
                headers: headers,
                body: formData,
                credentials: "same-origin",
            });

            if (response.ok) {
                const result = await response.json();
                this.hideUploadProgress();

                // Store media data temporarily
                this.pendingMediaData = {
                    ...result,
                    caption: caption,
                    message: caption || `Mengirim ${result.media_type}`,
                };

                // Show product selector
                const modalElement = document.getElementById(
                    "product-selector-modal",
                );
                const modal = new bootstrap.Modal(modalElement);
                modal.show();
            } else {
                let errorMessage = "Upload failed";
                // Try to get specific error message from response
                try {
                    const errorData = await response.json();
                    errorMessage =
                        errorData.error || `Upload failed (${response.status})`;
                } catch (e) {
                    // If response is not JSON, read as text
                    try {
                        const errorText = await response.text();
                        console.error("Non-JSON error response:", errorText);
                        if (response.status === 400) {
                            errorMessage =
                                "Format file tidak didukung atau ukuran terlalu besar (maksimal 10MB)";
                        } else if (response.status === 500) {
                            errorMessage =
                                "Server error - masalah direktori upload";
                        } else {
                            errorMessage = `Server error (${response.status}). Silakan coba lagi.`;
                        }
                    } catch (textError) {
                        console.error(
                            "Could not read response text:",
                            textError,
                        );
                        errorMessage = `Server error (${response.status}). Silakan coba lagi.`;
                    }
                }
                throw new Error(errorMessage);
            }
        } catch (error) {
            console.error("Media upload error:", error);
            this.hideUploadProgress();
            alert("Gagal upload media: " + error.message);
        } finally {
            // Clean up pending file reference regardless of success or failure
            this.pendingMediaFile = null;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return "0 Bytes";
        const k = 1024;
        const sizes = ["Bytes", "KB", "MB", "GB"];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
    }

    sendMediaMessage(mediaData, caption = "") {
        if (!this.isConnected) {
            this.displaySystemMessage(
                "Chat tidak terhubung. Mencoba menyambung kembali...",
                "warning",
            );
            this.setupWebSocket();
            return;
        }

        const messageInput = document.getElementById("chat-message-input");
        const messageText = caption || messageInput.value.trim();

        const messageDataToSend = {
            type: "chat_message",
            message: messageText || `Mengirim ${mediaData.media_type}`,
            product_id: this.selectedProduct ? this.selectedProduct.id : null,
            media_data: {
                media_url: mediaData.media_url,
                media_type: mediaData.media_type,
                media_filename: mediaData.filename,
            },
        };

        this.ws.send(JSON.stringify(messageDataToSend));
        messageInput.value = "";

        // Clear product tag after sending
        if (this.selectedProduct) {
            this.clearProductTag();
        }

        // Clear pending media data
        this.pendingMediaData = null;
    }

    showUploadProgress() {
        const progressDiv = document.createElement("div");
        progressDiv.id = "upload-progress";
        progressDiv.className = "upload-progress";
        progressDiv.innerHTML = `
            <div class="upload-progress-content">
                <div class="spinner-border spinner-border-sm text-primary" role="status"></div>
                <span class="ms-2">Uploading media...</span>
            </div>
        `;

        const chatInput = document.querySelector(".chat-input-container");
        if (chatInput) {
            chatInput.appendChild(progressDiv);
        }
    }

    hideUploadProgress() {
        const progressDiv = document.getElementById("upload-progress");
        if (progressDiv) {
            progressDiv.remove();
        }
    }

    escapeHtml(text) {
        const div = document.createElement("div");
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for HTML onclick events
function toggleChatOrContactModal() {
    // Check if user is logged in as buyer
    if (window.floatingChat && window.floatingChat.currentUser && window.floatingChat.currentUser.role === 'buyer') {
        toggleChat();
    } else {
        // Show contact modal for non-logged in users
        const contactModal = document.getElementById('contact-us-modal');
        const chatWindow = document.getElementById('chat-window');
        
        if (contactModal) {
            const isVisible = contactModal.style.display !== 'none';
            contactModal.style.display = isVisible ? 'none' : 'block';
            if (chatWindow) chatWindow.style.display = 'none';
        }
    }
}

function closeContactModal() {
    const contactModal = document.getElementById('contact-us-modal');
    if (contactModal) {
        contactModal.style.display = 'none';
    }
}

function toggleChat() {
    const chatWindow = document.getElementById("chat-window");
    const contactModal = document.getElementById("contact-us-modal");
    const isVisible = chatWindow.style.display !== "none";

    if (isVisible) {
        chatWindow.style.display = "none";
    } else {
        chatWindow.style.display = "block";
        if (contactModal) contactModal.style.display = 'none';
        // Reset unread count when opening chat
        if (window.floatingChat) {
            window.floatingChat.unreadCount = 0;
            window.floatingChat.updateChatBadge();
        }
    }
}

function handleChatKeyPress(event) {
    if (window.floatingChat) {
        window.floatingChat.handleChatKeyPress(event);
    }
}

function sendChatMessage() {
    if (window.floatingChat) {
        window.floatingChat.sendChatMessage();
    }
}

function handleTyping() {
    if (window.floatingChat) {
        window.floatingChat.handleTyping();
    }
}

function showProductSelector() {
    const modalElement = document.getElementById("product-selector-modal");
    if (modalElement) {
        const modal = new bootstrap.Modal(modalElement);
        modal.show();
    } else {
        console.error("Product selector modal not found.");
    }
}

function searchProducts() {
    if (window.floatingChat) {
        window.floatingChat.searchProducts();
    }
}

function clearProductTag() {
    if (window.floatingChat) {
        window.floatingChat.clearProductTag();
    }
}

// Request notification permission on first interaction or page load
if (Notification.permission === "default") {
    // Consider requesting permission on user interaction for better UX
    // For now, request on load if default
    Notification.requestPermission();
}

// Initialize chat when page loads
window.floatingChat = new FloatingChat();