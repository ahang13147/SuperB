// 切换编辑模式
function toggleEditMode() {
  const inputs = document.querySelectorAll('#profile-form input');
  const editBtn = document.getElementById('edit-btn');
  const saveBtn = document.getElementById('save-btn');
  const cancelBtn = document.getElementById('cancel-btn');

  inputs.forEach(input => {
    input.disabled = !input.disabled;
  });

  editBtn.style.display = 'none';
  saveBtn.style.display = 'inline-block';
  cancelBtn.style.display = 'inline-block';
}

// 取消编辑模式
function cancelEditMode() {
  const inputs = document.querySelectorAll('#profile-form input');
  const editBtn = document.getElementById('edit-btn');
  const saveBtn = document.getElementById('save-btn');
  const cancelBtn = document.getElementById('cancel-btn');

  inputs.forEach(input => {
    input.disabled = true;
  });

  editBtn.style.display = 'inline-block';
  saveBtn.style.display = 'none';
  cancelBtn.style.display = 'none';
}

// 处理表单提交
document.getElementById('profile-form').addEventListener('submit', function (event) {
  event.preventDefault();
  alert('Profile updated successfully!');
  cancelEditMode();
});

// 触发文件输入
function triggerFileInput() {
  document.getElementById('file-input').click();
}

// 处理图片上传
function handleImageUpload(event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      document.getElementById('profile-image').src = e.target.result;
    };
    reader.readAsDataURL(file);
  }
}