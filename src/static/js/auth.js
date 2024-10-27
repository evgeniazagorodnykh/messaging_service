// Показ формы регистрации
function showRegister() {
    document.getElementById('loginForm').style.display = 'none';
    document.getElementById('registerForm').style.display = 'block';
}

// Показ формы входа
function showLogin() {
    document.getElementById('registerForm').style.display = 'none';
    document.getElementById('loginForm').style.display = 'block';
}

// Обработка клика на кнопку "Войти"
function login() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    handleFormSubmit('login', 'login', [email, password]);
}

// Обработка клика на кнопку "Зарегистрироваться"
function register() {
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;

    handleFormSubmit('register', 'register', [email, username, password]);
}

// Обработка кликов по вкладкам (если используется)
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => showTab(tab.dataset.tab));
});

function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.form').forEach(form => form.classList.remove('active'));

    document.querySelector(`.tab[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}Form`).classList.add('active');
}

const validateForm = fields => fields.every(field => field.trim() !== '');

const sendRequest = async (url, data) => {
    try {
        const urlEncodedData = new URLSearchParams(data).toString();
        console.log(JSON.stringify(data))
        const response = await fetch('auth/' + url, {
            method: "POST",
            headers: {"Content-Type": "application/x-www-form-urlencoded",},
            body: urlEncodedData
        });

        if (response.ok) {
            alert('Операция выполнена успешно!');
            return true;
        } else {
            const result = await response.json().catch(() => ({}));
            alert(result.message || 'Ошибка выполнения запроса!');
            return null;
        }
    } catch (error) {
        console.error("Ошибка:", error);
        alert('Произошла ошибка на сервере');
    }
};

const handleFormSubmit = async (formType, url, fields) => {
    if (!validateForm(fields)) {
        alert('Пожалуйста, заполните все поля.');
        return;
    }

    const data = await sendRequest(url, formType === 'login'
        ? {username: fields[0], password: fields[1]}
        : {email: fields[0], username: fields[1], password: fields[2]});

    if (data && formType === 'login') {
        window.location.href = '/';
    }
};
