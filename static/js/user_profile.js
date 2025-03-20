// Configures constants
const API_BASE = 'http://localhost:8000';
const DEFAULT_USER_ID = 3;

// Initialize the page
document.addEventListener('DOMContentLoaded', initializeProfile);

// Main initialization function
async function initializeProfile() {
    try {
        const user = await fetchUserData();
        updateProfileUI(user);
    } catch (error) {
        showError(error.message);
    }
}

// Get user data
async function fetchUserData() {
    try {
        const response = await fetch(`${API_BASE}/get_user`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
            // body: JSON.stringify({ user_id: DEFAULT_USER_ID }),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to fetch user data');
        }

        const data = await response.json();
        if (data.status !== 'success') {
            throw new Error(data.error || 'API response error');
        }
        return data.data;
    } catch (error) {
        console.error('Fetch user error:', error);
        throw new Error('Failed to load profile. Please try later.');
    }
}

// Update the interface
function updateProfileUI(user) {
    document.getElementById('username').textContent = user.username;
    document.getElementById('user-id').textContent = `User ID: ${user.user_id}`;
    document.getElementById('role-type').textContent = `(${user.role})`;
    document.getElementById('full-name').value = user.username;
    document.getElementById('email').value = user.email;
    document.getElementById('phone').value = user.phone_number;
}

// Edit mode switch
function toggleEditMode() {
    const inputs = document.querySelectorAll('#profile-form input');
    inputs.forEach(input => input.disabled = false);
    document.getElementById('edit-btn').style.display = 'none';
    document.getElementById('save-btn').style.display = 'inline-block';
    document.getElementById('cancel-btn').style.display = 'inline-block';
}
// Cancel the edit
function cancelEditMode() {
    document.querySelectorAll('#profile-form input').forEach(input => {
        input.disabled = true;
    });

    document.getElementById('edit-btn').style.display = 'inline-block';
    document.getElementById('save-btn').style.display = 'none';
    document.getElementById('cancel-btn').style.display = 'none';

    // Restore original data
    initializeProfile();
}

// Form submission processing
document.addEventListener('DOMContentLoaded', function() {
    const profileForm = document.getElementById('profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            try {
                await updateUserProfile();
            } catch (error) {
                showError(error.message);
            }
        });
    } else {
        console.error('Profile form not found!');
    }
});

// Update user profile
async function updateUserProfile() {
    const updateData = {
        user_id: DEFAULT_USER_ID,
        username: document.getElementById('full-name').value,
        email: document.getElementById('email').value,
        phone_number: document.getElementById('phone').value
    };

    try {
        const response = await fetch(`${API_BASE}/update_user`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(updateData),
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Update failed');
        }

        const data = await response.json();
        handleUpdateSuccess(data);
    } catch (error) {
        console.error('Update error:', error);
        throw new Error('Failed to update profile. Please try later.');
    }
}

// The update was processed successfully
function handleUpdateSuccess(response) {
    if (response.message.includes('No changes')) {
        alert('Profile information unchanged');
    } else {
        alert('Profile updated successfully!');
        initializeProfile();
    }
    cancelEditMode();
}

// Error handling
function showError(message) {
    const errorContainer = document.createElement('div');
    errorContainer.className = 'global-error';
    errorContainer.innerHTML = `
        <div class="error-alert">
            <i class="fas fa-exclamation-circle"></i>
            ${message}
        </div>
    `;
    document.body.prepend(errorContainer);
    setTimeout(() => errorContainer.remove(), 5000);
}

// Image upload function
function triggerFileInput() {
    document.getElementById('file-input').click();
}

function handleImageUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
        document.getElementById('profile-image').src = e.target.result;
    };
    reader.readAsDataURL(file);
}


//add for menu
document.addEventListener('DOMContentLoaded', function() {
    const hamburger = document.querySelector('.hamburger-menu');
    const sidebar = document.querySelector('.sidebar');

    // 汉堡菜单点击事件
    hamburger.addEventListener('click', function() {
        sidebar.classList.toggle('active');
    });

    // 点击外部关闭侧边栏
    document.addEventListener('click', function(e) {
        if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
            sidebar.classList.remove('active');
        }
    });

    // 窗口大小变化时重置侧边栏
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            sidebar.classList.remove('active');
        }
    });
});