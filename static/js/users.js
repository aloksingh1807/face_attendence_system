/* MEMBER DIRECTORY & ENROLLMENT WIZARD CONTROLLER */

document.addEventListener("DOMContentLoaded", function() {
    const directoryContainer = document.getElementById("users-directory-container");
    const searchInput = document.getElementById("user-search-input");
    
    // Modal Selectors
    const modal = document.getElementById("enroll-modal");
    const openModalBtn = document.getElementById("open-enroll-modal-btn");
    const closeModalBtn = document.getElementById("close-enroll-modal-btn");
    const cancelModalBtn = document.getElementById("cancel-enroll-btn");
    
    // Form Selectors
    const form = document.getElementById("enroll-user-form");
    const enrollName = document.getElementById("enroll-name");
    const enrollEmail = document.getElementById("enroll-email");
    const enrollRole = document.getElementById("enroll-role");
    
    // Camera Selectors
    const modalVideo = document.getElementById("modal-webcam");
    const captureCanvas = document.getElementById("modal-capture-canvas");
    const capturePreview = document.getElementById("capture-preview-img");
    const takePhotoBtn = document.getElementById("capture-snapshot-btn");
    const retakePhotoBtn = document.getElementById("reset-capture-btn");
    const submitBtn = document.getElementById("submit-enroll-btn");
    
    let modalStream = null;
    let base64CapturedFace = null;
    let registeredUsers = [];

    // 1. Fetch Directory Profiles
    function loadDirectory() {
        if (!directoryContainer) return;
        
        fetch('/api/users')
            .then(res => res.json())
            .then(data => {
                registeredUsers = data;
                renderDirectory(data);
            })
            .catch(err => {
                console.error("Directory fetch error:", err);
                directoryContainer.innerHTML = `
                    <div class="directory-error">
                        <i class="fa-solid fa-triangle-exclamation"></i>
                        <p>Failed to load member profiles directory.</p>
                    </div>
                `;
            });
    }

    function renderDirectory(users) {
        directoryContainer.innerHTML = "";
        
        // Remove administrators from public list display to prevent cluttering
        const employees = users.filter(u => u.role !== 'Admin');
        
        if (employees.length === 0) {
            directoryContainer.innerHTML = `
                <div class="directory-empty-state">
                    <i class="fa-solid fa-users-slash text-gradient"></i>
                    <p>No registered employees found. Click Register to enroll new faces.</p>
                </div>
            `;
            return;
        }
        
        employees.forEach(user => {
            const card = document.createElement("div");
            card.className = "user-card animate-fade-in";
            
            const avatarImg = user.photo_path 
                ? `/${user.photo_path}` 
                : "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde?auto=format&fit=crop&w=150&h=150";
                
            card.innerHTML = `
                <button class="user-delete-btn" onclick="deleteUserProfile(${user.id})" title="Delete Profile">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
                <img class="user-card-avatar" src="${avatarImg}" alt="${user.name}">
                <h4 class="user-card-name">${user.name}</h4>
                <p class="user-card-email">${user.email}</p>
                <span class="badge badge-primary">${user.role}</span>
            `;
            
            directoryContainer.appendChild(card);
        });
    }

    // 2. Client-side Search filter
    if (searchInput) {
        searchInput.addEventListener("input", function() {
            const val = this.value.toLowerCase();
            const filtered = registeredUsers.filter(u => 
                u.name.toLowerCase().includes(val) || 
                u.email.toLowerCase().includes(val)
            );
            renderDirectory(filtered);
        });
    }

    // 3. Modal open / close streams
    if (openModalBtn) {
        openModalBtn.addEventListener("click", function() {
            modal.classList.remove("hidden");
            startModalWebcam();
        });
    }

    function closeModal() {
        modal.classList.add("hidden");
        stopModalWebcam();
        resetEnrollForm();
    }

    if (closeModalBtn) closeModalBtn.addEventListener("click", closeModal);
    if (cancelModalBtn) cancelModalBtn.addEventListener("click", closeModal);

    // 4. Modal camera controls
    function startModalWebcam() {
        navigator.mediaDevices.getUserMedia({
            video: { width: 320, height: 240, facingMode: "user" },
            audio: false
        })
        .then(stream => {
            modalStream = stream;
            modalVideo.srcObject = stream;
            modalVideo.classList.remove("hidden");
            capturePreview.classList.add("hidden");
            takePhotoBtn.classList.remove("hidden");
            retakePhotoBtn.classList.add("hidden");
        })
        .catch(err => {
            console.error("Modal camera access failed:", err);
            showNotificationToast("Webcam access required for registration snapshots.", "danger");
        });
    }

    function stopModalWebcam() {
        if (modalStream) {
            modalStream.getTracks().forEach(track => track.stop());
            modalStream = null;
        }
    }

    if (takePhotoBtn) {
        takePhotoBtn.addEventListener("click", function() {
            if (!modalStream) return;
            
            const ctx = captureCanvas.getContext("2d");
            ctx.drawImage(modalVideo, 0, 0, captureCanvas.width, captureCanvas.height);
            
            base64CapturedFace = captureCanvas.toDataURL("image/jpeg", 0.9);
            
            capturePreview.src = base64CapturedFace;
            capturePreview.classList.remove("hidden");
            modalVideo.classList.add("hidden");
            
            takePhotoBtn.classList.add("hidden");
            retakePhotoBtn.classList.remove("hidden");
            submitBtn.removeAttribute("disabled");
        });
    }

    if (retakePhotoBtn) {
        retakePhotoBtn.addEventListener("click", function() {
            capturePreview.classList.add("hidden");
            modalVideo.classList.remove("hidden");
            takePhotoBtn.classList.remove("hidden");
            retakePhotoBtn.classList.add("hidden");
            submitBtn.setAttribute("disabled", "true");
            base64CapturedFace = null;
        });
    }

    // 5. Submit Registration forms
    if (form) {
        form.addEventListener("submit", function(e) {
            e.preventDefault();
            
            if (!base64CapturedFace) {
                showNotificationToast("Please capture a face snapshot first.", "warning");
                return;
            }
            
            submitBtn.setAttribute("disabled", "true");
            submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Registering...`;
            
            fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    name: enrollName.value,
                    email: enrollEmail.value,
                    role: enrollRole.value,
                    image: base64CapturedFace
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showNotificationToast("User registered successfully!", "success");
                    closeModal();
                    loadDirectory();
                } else {
                    showNotificationToast(data.error || "Failed registering user.", "danger");
                    submitBtn.removeAttribute("disabled");
                    submitBtn.innerHTML = `<i class="fa-solid fa-square-check"></i> Register Member`;
                }
            })
            .catch(err => {
                console.error("Submit user error:", err);
                showNotificationToast("Internal server error during enrollment.", "danger");
                submitBtn.removeAttribute("disabled");
                submitBtn.innerHTML = `<i class="fa-solid fa-square-check"></i> Register Member`;
            });
        });
    }

    function resetEnrollForm() {
        form.reset();
        base64CapturedFace = null;
        submitBtn.setAttribute("disabled", "true");
        submitBtn.innerHTML = `<i class="fa-solid fa-square-check"></i> Register Member`;
    }

    // Expose delete user function to global window context
    window.deleteUserProfile = function(userId) {
        if (!confirm("Are you sure you want to delete this user profile? This action will permanently remove their face recognition data.")) return;
        
        fetch(`/api/users/${userId}`, {
            method: 'DELETE'
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                showNotificationToast("User profile deleted successfully.", "success");
                loadDirectory();
            } else {
                showNotificationToast(data.error || "Failed deleting user.", "danger");
            }
        })
        .catch(err => {
            console.error("Delete user error:", err);
            showNotificationToast("Server error deleting user profile.", "danger");
        });
    };

    // Load directory initially
    loadDirectory();
});
