// // Page switching functionality
// document.querySelectorAll('.nav-item').forEach(item => {
//     item.addEventListener('click', function() {
//         // Remove all active states
//         document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
//         this.classList.add('active');
//
//         // Switch content display
//         const panels = document.querySelectorAll('.search-container, .notification-panel');
//         panels.forEach(p => p.style.display = 'none');
//
//         if(this.querySelector('.fa-bell')) {
//             document.querySelector('.notification-panel').style.display = 'block';
//         } else {
//             document.querySelector('.search-container').style.display = 'block';
//         }
//     });
// });