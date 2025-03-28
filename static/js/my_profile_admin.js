// Configures constants
const API_BASE = 'https://www.diicsu.top:8000'; // Change the IP address to the server address
const DEFAULT_USER_ID = 1;  // Default user ID, used for backup only

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    initializeProfile();

    // Make sure to bind events only after the DOM has loaded
    const form = document.getElementById('profile-form');
    if (form) {
        form.addEventListener('submit', handleFormSubmit);
    } else {
        console.error('无法找到profile-form表单元素');
    }
});

async function handleFormSubmit(e) {
    e.preventDefault();
    try {
        await updateUserProfile();
    } catch (error) {
        showError(error.message);
    }
}

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
            credentials: 'include' // Let the request carry a Cookie
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
    inputs.forEach(input => {
        if (input.id !== 'email') { // Skip the mailbox input box
            input.disabled = false;
        }
    });
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

// Update user profile
async function updateUserProfile() {
    const updateData = {
        user_id: DEFAULT_USER_ID, // You are advised to obtain the ID of the current user based on the session
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
            credentials: 'include',  // Carry Cookie
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

document.addEventListener('DOMContentLoaded', function() {
  // Process menu group click
  document.querySelectorAll('.group-header').forEach(header => {
    header.addEventListener('click', function() {
      const group = this.closest('.menu-group');
      group.classList.toggle('active');

      // Close other expanded menu groups
      document.querySelectorAll('.menu-group').forEach(otherGroup => {
        if (otherGroup !== group) {
          otherGroup.classList.remove('active');
        }
      });
    });
  });

  //Mobile burger menu switch
  const hamburger = document.querySelector('.hamburger-menu');
  const sidebar = document.querySelector('.sidebar');

  hamburger.addEventListener('click', function(e) {
    e.stopPropagation(); 
    sidebar.classList.toggle('active');
  });

  //Click outside to close the sidebar
  document.addEventListener('click', function(e) {
    if (sidebar.classList.contains('active') &&
        !e.target.closest('.sidebar') &&
        !e.target.closest('.hamburger-menu')) {
      sidebar.classList.remove('active');
    }
  });

  //Prevents clicking inside the sidebar from triggering closure
  sidebar.addEventListener('click', function(e) {
    e.stopPropagation();
  });
});
