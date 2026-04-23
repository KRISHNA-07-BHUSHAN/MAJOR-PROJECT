// ------------------- PASSWORD TOGGLE -------------------
const toggle = document.getElementById("togglePassword");
const pass = document.getElementById("passwordInput");

toggle.onclick = () => {
    pass.type = pass.type === "password" ? "text" : "password";
    toggle.textContent = pass.type === "password" ? "👁️" : "🙈";
};


// ------------------- EMAIL VALIDATION -------------------
const emailInput = document.getElementById("emailInput");
const emailError = document.getElementById("emailError");

function validateEmail() {
    let value = emailInput.value.trim();
    let pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!pattern.test(value)) {
        emailError.textContent = "Please enter a valid email address.";
        return false;
    }
    emailError.textContent = "";
    return true;
}

emailInput.addEventListener("input", validateEmail);


// ------------------- PASSWORD VALIDATION -------------------
const passwordError = document.getElementById("passwordError");

pass.addEventListener("focus", () => {
    passwordError.textContent = "Password must be at least 8 characters.";
    passwordError.classList.remove("valid");
});

function validatePassword() {
    const p = pass.value;

    passwordError.classList.remove("valid");

    if (p.length < 8) {
        passwordError.textContent = "Password must be at least 8 characters.";
        return false;
    }

    if (!/[A-Z]/.test(p)) {
        passwordError.textContent = "Password must contain an uppercase letter.";
        return false;
    }

    if (!/[0-9]/.test(p)) {
        passwordError.textContent = "Password must include a number.";
        return false;
    }

    if (!/[@_]/.test(p)) {
        passwordError.textContent = "Password must contain @ or _ symbol.";
        return false;
    }

    if (!/^[A-Za-z0-9@_]+$/.test(p)) {
        passwordError.textContent = "Only letters, numbers, @ and _ are allowed.";
        return false;
    }

    passwordError.textContent = "Password is strong.";
    passwordError.classList.add("valid");
    return true;
}

pass.addEventListener("input", validatePassword);


// ------------------- ADMIN LIST -------------------
const adminAccounts = [
    { email: "admin070@gmail.com", password: "Admin@070" },
    { email: "admin119@gmail.com", password: "Admin@119" },
    { email: "admin022@gmail.com", password: "Admin@022" },
    { email: "admin053@gmail.com", password: "Admin@053" }
];

function isAdmin(email, password) {
    return adminAccounts.some(acc => acc.email === email && acc.password === password);
}


// ------------------- LOGIN BUTTON -------------------
document.getElementById("loginBtn").onclick = () => {

    if (!validateEmail() || !validatePassword()) {
        alert("Please enter valid email & password.");
        return;
    }

    const email = emailInput.value.trim();
    const password = pass.value.trim();

    const adminBtn = document.getElementById("btnGuardian");
    const userBtn = document.getElementById("btnAnalyst");

    // Default: disable admin, enable user
    adminBtn.disabled = true;
    adminBtn.style.opacity = "0.5";

    userBtn.disabled = false;
    userBtn.style.opacity = "1";

    // If admin → enable admin + disable analyst
    if (isAdmin(email, password)) {
        adminBtn.disabled = false;
        adminBtn.style.opacity = "1";
        userBtn.disabled = true;
        userBtn.style.opacity = "0.5";
    }

    // Show role modal
    document.getElementById("roleModal").style.display = "flex";
};


// ------------------- ROLE MODAL BUTTON HANDLERS -------------------
document.getElementById("closeModal").onclick = () => {
    document.getElementById("roleModal").style.display = "none";
};

document.getElementById("btnGuardian").onclick = () => {
    const email = emailInput.value.trim();
    const password = pass.value.trim();

    if (!isAdmin(email, password)) {
        alert("You are not an admin");
        return;
    }

    alert("Welcome Sentinel Guardian (Admin Role)");
    window.location.href = "dashboard.html";
};

document.getElementById("btnAnalyst").onclick = () => {
    const email = emailInput.value.trim();
    const password = pass.value.trim();

    if (isAdmin(email, password)) {
        alert("Admins cannot register as users.");
        return;
    }

    alert("Welcome Cloud Analyst (User Role)");
    window.location.href = "register.html";
};


// ------------------- FORGOT PASSWORD HANDLER -------------------
document.querySelector(".links a").onclick = (e) => {
    e.preventDefault();
    document.getElementById("forgotModal").style.display = "flex";
};

document.getElementById("closeForgot").onclick = () => {
    document.getElementById("forgotModal").style.display = "none";
    document.getElementById("forgotError").textContent = "";
    document.getElementById("forgotEmail").value = "";
};

document.getElementById("forgotSubmit").onclick = () => {
    const emailBox = document.getElementById("forgotEmail");
    const errorBox = document.getElementById("forgotError");
    const email = emailBox.value.trim();

    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    if (!pattern.test(email)) {
        errorBox.textContent = "Enter a valid email address.";
        return;
    }

    if (adminAccounts.some(acc => acc.email === email)) {
        errorBox.textContent = "Admin accounts cannot reset password here.";
        return;
    }

    errorBox.textContent = "";
    alert("A password reset link has been sent to: " + email);

    document.getElementById("forgotModal").style.display = "none";
};
