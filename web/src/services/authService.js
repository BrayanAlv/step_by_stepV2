const API_URL = 'https://stepbystep.cv/api';

/**
 * Inicia sesión enviando credenciales x-www-form-urlencoded
 */
export async function login(email, password) {
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch(`${API_URL}/auth/login`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error al iniciar sesión');
    }

    const data = await response.json();

    if (data.access_token) {
        localStorage.setItem('token', data.access_token);

        // guardar userId
        sessionStorage.setItem("userId", data.user?.id);
    }

    return data;
}

/**
 * Registra un nuevo usuario enviando JSON
 */
export async function register(userData) {
    const response = await fetch(`${API_URL}/auth/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
    });

    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error al registrar usuario');
    }

    const data = await response.json();

    if (data.access_token) {
        localStorage.setItem('token', data.access_token);
    }

    return data;
}

/**
 * Cierra sesión eliminando el token
 */
export function logout() {
    localStorage.removeItem('token');
    sessionStorage.removeItem('userId'); //importante si usas header dinámico
}

/**
 * Verifica si existe un token en localStorage
 */
export function isAuthenticated() {
    return !!localStorage.getItem('token');
}

/**
 * Obtiene el token actual
 */
export function getToken() {
    return localStorage.getItem('token');
}

// const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// /**
//  * Inicia sesión enviando credenciales x-www-form-urlencoded
//  */
// export async function login(email, password) {
//     const formData = new URLSearchParams();
//     formData.append('username', email);
//     formData.append('password', password);

//     const response = await fetch(`${API_URL}/auth/login`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/x-www-form-urlencoded',
//         },
//         body: formData,
//     });

//     if (!response.ok) {
//         const errorData = await response.json().catch(() => ({}));
//         throw new Error(errorData.detail || 'Error al iniciar sesión');
//     }

//     const data = await response.json();
//     if (data.access_token) {
//         localStorage.setItem('token', data.access_token);
//     }
//     return data;
// }

// /**
//  * Registra un nuevo usuario enviando JSON
//  */
// export async function register(userData) {
//     const response = await fetch(`${API_URL}/auth/register`, {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify(userData),
//     });

//     if (!response.ok) {
//         const errorData = await response.json().catch(() => ({}));
//         throw new Error(errorData.detail || 'Error al registrar usuario');
//     }

//     const data = await response.json();
//     if (data.access_token) {
//         localStorage.setItem('token', data.access_token);
//     }
//     return data;
// }

// /**
//  * Cierra sesión eliminando el token
//  */
// export function logout() {
//     localStorage.removeItem('token');
// }

// /**
//  * Verifica si existe un token en localStorage
//  */
// export function isAuthenticated() {
//     return !!localStorage.getItem('token');
// }

// /**
//  * Obtiene el token actual
//  */
// export function getToken() {
//     return localStorage.getItem('token');
// }
