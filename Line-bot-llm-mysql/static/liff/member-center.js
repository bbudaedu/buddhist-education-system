/**
 * LIFF Member Center JavaScript
 * 會員中心前端邏輯
 */

// Configuration
const LIFF_ID = '2008639772-ndVeDxwD';
const API_BASE_URL = '/api/member';

// State
let userProfile = null;
let userPreferences = null;

// DOM Elements
const elements = {
    loading: document.getElementById('loading'),
    error: document.getElementById('error'),
    errorMessage: document.getElementById('error-message'),
    mainContent: document.getElementById('main-content'),
    profilePicture: document.getElementById('profile-picture'),
    profileName: document.getElementById('profile-name'),
    profileStatus: document.getElementById('profile-status'),
    emailDisplay: document.getElementById('email-display'),
    currentEmail: document.getElementById('current-email'),
    emailVerifiedBadge: document.getElementById('email-verified-badge'),
    emailInputSection: document.getElementById('email-input-section'),
    emailInput: document.getElementById('email-input'),
    sendVerificationBtn: document.getElementById('send-verification-btn'),
    verificationSection: document.getElementById('verification-section'),
    verificationCode: document.getElementById('verification-code'),
    verifyBtn: document.getElementById('verify-btn'),
    channelEmail: document.getElementById('channel-email'),
    channelWebpush: document.getElementById('channel-webpush'),
    contentBooks: document.getElementById('content-books'),
    contentVideos: document.getElementById('content-videos'),
    contentLivestream: document.getElementById('content-livestream'),
    contentNews: document.getElementById('content-news'),
    saveBtn: document.getElementById('save-btn'),
    closeBtn: document.getElementById('close-btn'),
    toast: document.getElementById('toast')
};

// Initialize LIFF
async function initializeLiff() {
    try {
        await liff.init({ liffId: LIFF_ID });

        if (!liff.isLoggedIn()) {
            liff.login();
            return;
        }

        await loadUserProfile();
        await loadUserPreferences();
        await loadNotificationChannels();

        showMainContent();
    } catch (error) {
        console.error('LIFF initialization failed:', error);
        showError('初始化失敗：' + error.message);
    }
}

// Load user profile from LINE
async function loadUserProfile() {
    try {
        userProfile = await liff.getProfile();

        // Update UI
        elements.profileName.textContent = userProfile.displayName;
        elements.profilePicture.src = userProfile.pictureUrl || '';

        // Try to get email from ID token
        const idToken = liff.getDecodedIDToken();
        console.log('ID Token:', idToken); // 除錯用

        if (idToken && idToken.email) {
            console.log('Email from LINE:', idToken.email); // 除錯用
            elements.emailInput.value = idToken.email;
            elements.emailInput.disabled = true;
            elements.emailInputSection.innerHTML = `
                <p>您的 Email：<strong>${idToken.email}</strong></p>
                <span class="badge badge-success">✓ LINE 已驗證</span>
            `;
        } else {
            console.log('No email in ID Token'); // 除錯用
        }
    } catch (error) {
        console.error('Failed to load profile:', error);
    }
}

// Load user preferences from API
async function loadUserPreferences() {
    try {
        const response = await fetch(`${API_BASE_URL}/preferences`, {
            headers: {
                'Authorization': `Bearer ${liff.getAccessToken()}`
            }
        });

        if (response.ok) {
            userPreferences = await response.json();
            applyPreferences();
        }
    } catch (error) {
        console.error('Failed to load preferences:', error);
    }
}

/**
 * 載入可用的通知管道配置
 * 根據後端配置動態顯示/隱藏通知選項
 */
async function loadNotificationChannels() {
    try {
        const response = await fetch(`${API_BASE_URL}/notification-channels`);

        if (response.ok) {
            const data = await response.json();
            const channels = data.channels;

            // 根據配置顯示/隱藏選項
            if (channels.line) {
                document.getElementById('channel-line-wrapper')?.classList.remove('hidden');
            }
            if (channels.email) {
                document.getElementById('channel-email-wrapper')?.classList.remove('hidden');
            }
            if (channels.webpush) {
                document.getElementById('channel-webpush-wrapper')?.classList.remove('hidden');
            }

            console.log('Notification channels loaded:', channels);
        } else {
            // API 失敗時預設顯示 Email 選項
            document.getElementById('channel-email-wrapper')?.classList.remove('hidden');
            console.warn('Failed to load notification channels, showing email as default');
        }
    } catch (error) {
        console.error('Failed to load notification channels:', error);
        // 錯誤時預設顯示 Email 選項
        document.getElementById('channel-email-wrapper')?.classList.remove('hidden');
    }
}

// Apply preferences to UI
function applyPreferences() {
    if (!userPreferences) return;

    // Email settings
    if (userPreferences.email) {
        elements.emailDisplay.classList.remove('hidden');
        elements.currentEmail.textContent = userPreferences.email;
        elements.emailInputSection.classList.add('hidden');

        if (userPreferences.emailVerified) {
            elements.emailVerifiedBadge.classList.remove('hidden');
        }
    }

    // Notification channels
    const channels = userPreferences.notificationChannels || ['line'];
    elements.channelEmail.checked = channels.includes('email');
    elements.channelWebpush.checked = channels.includes('webpush');

    // Content preferences
    const contentTypes = userPreferences.preferredContentTypes || [];
    elements.contentBooks.checked = contentTypes.includes('books');
    elements.contentVideos.checked = contentTypes.includes('videos');
    elements.contentLivestream.checked = contentTypes.includes('livestream');
    elements.contentNews.checked = contentTypes.includes('news');

    // Notification frequency
    const frequency = userPreferences.notificationFrequency || 'realtime';
    document.querySelector(`input[name="frequency"][value="${frequency}"]`).checked = true;
}

// Send verification email
async function sendVerificationEmail() {
    const email = elements.emailInput.value.trim();

    if (!email || !isValidEmail(email)) {
        showToast('請輸入有效的 Email 地址');
        return;
    }

    elements.sendVerificationBtn.disabled = true;
    elements.sendVerificationBtn.textContent = '發送中...';

    try {
        const response = await fetch(`${API_BASE_URL}/send-verification`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${liff.getAccessToken()}`
            },
            body: JSON.stringify({ email })
        });

        if (response.ok) {
            elements.verificationSection.classList.remove('hidden');
            showToast('驗證碼已發送至您的 Email');
        } else {
            const data = await response.json();
            showToast(data.error || '發送失敗，請稍後再試');
        }
    } catch (error) {
        showToast('發送失敗：' + error.message);
    } finally {
        elements.sendVerificationBtn.disabled = false;
        elements.sendVerificationBtn.textContent = '發送驗證碼';
    }
}

// Verify email code
async function verifyEmailCode() {
    const code = elements.verificationCode.value.trim();

    if (!code || code.length < 4) {
        showToast('請輸入驗證碼');
        return;
    }

    elements.verifyBtn.disabled = true;
    elements.verifyBtn.textContent = '驗證中...';

    try {
        const response = await fetch(`${API_BASE_URL}/verify-email`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${liff.getAccessToken()}`
            },
            body: JSON.stringify({
                email: elements.emailInput.value.trim(),
                code
            })
        });

        if (response.ok) {
            elements.emailDisplay.classList.remove('hidden');
            elements.currentEmail.textContent = elements.emailInput.value;
            elements.emailVerifiedBadge.classList.remove('hidden');
            elements.emailInputSection.classList.add('hidden');
            elements.verificationSection.classList.add('hidden');
            showToast('Email 驗證成功！');
        } else {
            const data = await response.json();
            showToast(data.error || '驗證碼錯誤');
        }
    } catch (error) {
        showToast('驗證失敗：' + error.message);
    } finally {
        elements.verifyBtn.disabled = false;
        elements.verifyBtn.textContent = '驗證';
    }
}

// Save preferences
async function savePreferences() {
    elements.saveBtn.disabled = true;
    elements.saveBtn.textContent = '儲存中...';

    const preferences = {
        notificationChannels: ['line'],
        preferredContentTypes: [],
        notificationFrequency: document.querySelector('input[name="frequency"]:checked').value
    };

    // Collect notification channels
    if (elements.channelEmail.checked) preferences.notificationChannels.push('email');
    if (elements.channelWebpush.checked) preferences.notificationChannels.push('webpush');

    // Collect content types
    if (elements.contentBooks.checked) preferences.preferredContentTypes.push('books');
    if (elements.contentVideos.checked) preferences.preferredContentTypes.push('videos');
    if (elements.contentLivestream.checked) preferences.preferredContentTypes.push('livestream');
    if (elements.contentNews.checked) preferences.preferredContentTypes.push('news');

    try {
        const response = await fetch(`${API_BASE_URL}/preferences`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${liff.getAccessToken()}`
            },
            body: JSON.stringify(preferences)
        });

        if (response.ok) {
            showToast('設定已儲存！');
        } else {
            const data = await response.json();
            showToast(data.error || '儲存失敗');
        }
    } catch (error) {
        showToast('儲存失敗：' + error.message);
    } finally {
        elements.saveBtn.disabled = false;
        elements.saveBtn.textContent = '儲存設定';
    }
}

// Close LIFF
function closeLiff() {
    if (liff.isInClient()) {
        liff.closeWindow();
    } else {
        window.close();
    }
}

// UI Helpers
function showMainContent() {
    elements.loading.classList.add('hidden');
    elements.mainContent.classList.remove('hidden');
}

function showError(message) {
    elements.loading.classList.add('hidden');
    elements.errorMessage.textContent = message;
    elements.error.classList.remove('hidden');
}

function showToast(message) {
    elements.toast.textContent = message;
    elements.toast.classList.remove('hidden');
    setTimeout(() => elements.toast.classList.add('hidden'), 3000);
}

function isValidEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Event Listeners
elements.sendVerificationBtn?.addEventListener('click', sendVerificationEmail);
elements.verifyBtn?.addEventListener('click', verifyEmailCode);
elements.saveBtn?.addEventListener('click', savePreferences);
elements.closeBtn?.addEventListener('click', closeLiff);

// Initialize
document.addEventListener('DOMContentLoaded', initializeLiff);
