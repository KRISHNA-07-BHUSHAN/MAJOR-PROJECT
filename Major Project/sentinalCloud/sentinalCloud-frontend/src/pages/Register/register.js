// ------------------- ADMIN BLOCK LIST -------------------
const adminAccounts = [
    { email: "admin070@gmail.com", password: "Admin@070" },
    { email: "admin119@gmail.com", password: "Admin@119" },
    { email: "admin022@gmail.com", password: "Admin@022" },
    { email: "admin053@gmail.com", password: "Admin@053" }
];

function isAdmin(email, password) {
    return adminAccounts.some(acc => acc.email === email && acc.password === password);
}

// ------------------- ELEMENTS -------------------
const fullName = document.getElementById("fullName");
const dob = document.getElementById("dobInput");
const email = document.getElementById("emailInput");
const password = document.getElementById("passwordInput");
const confirmPass = document.getElementById("confirmPassword");
const phone = document.getElementById("phoneInput");
const org = document.getElementById("orgInput");

// Error labels
const nameError = document.getElementById("nameError");
const dobError = document.getElementById("dobError");
const emailError = document.getElementById("emailError");
const passwordError = document.getElementById("passwordError");
const confirmError = document.getElementById("confirmError");

// ------------------- TOGGLE PASSWORD -------------------
document.getElementById("togglePassword").onclick = () => {
    password.type = password.type === "password" ? "text" : "password";
};

// ------------------- LIVE EMAIL VALIDATION -------------------
email.addEventListener("input", () => {
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    emailError.textContent = 
        pattern.test(email.value.trim())
        ? ""
        : "Please enter a valid email address.";
});

// ------------------- PASSWORD VALIDATION -------------------
password.addEventListener("focus", () => {
    passwordError.textContent = "Password must be at least 8 characters.";
    passwordError.classList.remove("valid");
});

function validatePassword() {
    const p = password.value.trim();

    // Always remove green styling first
    passwordError.classList.remove("valid");

    // Rule 1 — length
    if (p.length < 8) {
        passwordError.textContent = "Password must be at least 8 characters.";
        return false;
    }

    // Rule 2 — uppercase
    if (!/[A-Z]/.test(p)) {
        passwordError.textContent = "Password must contain an uppercase letter.";
        return false;
    }

    // Rule 3 — number
    if (!/[0-9]/.test(p)) {
        passwordError.textContent = "Password must include a number.";
        return false;
    }

    // Rule 4 — MUST contain @ or _
    if (!/[@_]/.test(p)) {
        passwordError.textContent = "Password must contain @ or _ symbol.";
        return false;
    }

    // Rule 5 — ONLY allowed characters
    if (!/^[A-Za-z0-9@_]+$/.test(p)) {
        passwordError.textContent = "Only letters, numbers, @ and _ are allowed.";
        return false;
    }

    // FINAL — Strong password
    passwordError.textContent = "Password is strong.";
    passwordError.classList.add("valid");   // turns GREEN
    return true;
}

password.addEventListener("input", validatePassword);


// ------------------- CONFIRM PASSWORD LIVE VALIDATION -------------------
confirmPass.addEventListener("input", () => {
    confirmError.textContent =
        confirmPass.value.trim() === password.value.trim()
            ? ""
            : "Passwords do not match.";
});

// ------------------- MAIN VALIDATION (ON REGISTER CLICK) -------------------
function validateRegister() {
    let valid = true;

    // Full Name
    if (fullName.value.trim() === "") {
        nameError.textContent = "Full name is required.";
        valid = false;
    } else {
        nameError.textContent = "";
    }

    // Date of Birth
    if (dob.value === "") {
        dobError.textContent = "Date of Birth is required.";
        valid = false;
    } else {
        dobError.textContent = "";
    }

    // Email
    const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailPattern.test(email.value.trim())) {
        emailError.textContent = "Enter a valid email.";
        valid = false;
    }

    // Admin restriction
    if (isAdmin(email.value.trim(), password.value.trim())) {
        alert("Admins cannot register here.");
        return false;
    }

    // Password validation
    if (!validatePassword()) {
        valid = false;
    }

    // Confirm Password
    if (confirmPass.value.trim() !== password.value.trim()) {
        confirmError.textContent = "Passwords do not match.";
        valid = false;
    } else {
        confirmError.textContent = "";
    }

    return valid;
}

// ------------------- REGISTER BUTTON -------------------
document.getElementById("registerBtn").onclick = () => {
    if (!validateRegister()) return;

    alert("Registration Successful!");
    window.location.href = "login.html";
};
