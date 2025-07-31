/**
 * Validaciones JavaScript para el sistema de aerolínea.
 * 
 * Este archivo contiene validaciones del lado cliente para:
 * - Formularios de reserva
 * - Validación de fechas
 * - Validación de asientos
 * - Validaciones en tiempo real
 */

// Configuración global
const VALIDATION_CONFIG = {
    minPasswordLength: 8,
    maxReservationDays: 365, // Máximo 1 año de anticipación
    minReservationHours: 2,  // Mínimo 2 horas antes del vuelo
    maxPassengersPerReservation: 10,
};

/**
 * Validaciones de formularios
 */
class FormValidator {
    constructor(formId) {
        this.form = document.getElementById(formId);
        this.errors = [];
        this.init();
    }
    
    init() {
        if (this.form) {
            this.setupEventListeners();
        }
    }
    
    setupEventListeners() {
        // Validación en tiempo real para campos de texto
        const textInputs = this.form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
        textInputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
        
        // Validación para fechas
        const dateInputs = this.form.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => {
            input.addEventListener('change', () => this.validateDate(input));
        });
        
        // Validación para números
        const numberInputs = this.form.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => {
            input.addEventListener('blur', () => this.validateNumber(input));
        });
        
        // Validación al enviar el formulario
        this.form.addEventListener('submit', (e) => this.validateForm(e));
    }
    
    validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        
        // Limpiar errores previos
        this.clearFieldError(field);
        
        // Validaciones específicas por tipo de campo
        switch (fieldName) {
            case 'username':
                if (value.length < 3) {
                    this.showFieldError(field, 'El nombre de usuario debe tener al menos 3 caracteres.');
                }
                break;
                
            case 'email':
                if (!this.isValidEmail(value)) {
                    this.showFieldError(field, 'Por favor, ingresa un email válido.');
                }
                break;
                
            case 'password1':
                if (value.length < VALIDATION_CONFIG.minPasswordLength) {
                    this.showFieldError(field, `La contraseña debe tener al menos ${VALIDATION_CONFIG.minPasswordLength} caracteres.`);
                }
                break;
                
            case 'password2':
                const password1 = this.form.querySelector('[name="password1"]').value;
                if (value !== password1) {
                    this.showFieldError(field, 'Las contraseñas no coinciden.');
                }
                break;
                
            case 'documento':
                if (!this.isValidDocument(value)) {
                    this.showFieldError(field, 'Por favor, ingresa un documento válido.');
                }
                break;
                
            case 'telefono':
                if (value && !this.isValidPhone(value)) {
                    this.showFieldError(field, 'Por favor, ingresa un teléfono válido.');
                }
                break;
        }
    }
    
    validateDate(field) {
        const selectedDate = new Date(field.value);
        const today = new Date();
        const fieldName = field.name;
        
        this.clearFieldError(field);
        
        switch (fieldName) {
            case 'fecha_nacimiento':
                const age = today.getFullYear() - selectedDate.getFullYear();
                if (age < 0 || age > 120) {
                    this.showFieldError(field, 'Por favor, ingresa una fecha de nacimiento válida.');
                }
                break;
                
            case 'fecha_salida':
                if (selectedDate <= today) {
                    this.showFieldError(field, 'La fecha de salida debe ser posterior a hoy.');
                }
                break;
        }
    }
    
    validateNumber(field) {
        const value = parseFloat(field.value);
        const fieldName = field.name;
        
        this.clearFieldError(field);
        
        switch (fieldName) {
            case 'precio':
                if (value <= 0) {
                    this.showFieldError(field, 'El precio debe ser mayor a 0.');
                }
                break;
                
            case 'capacidad':
                if (value <= 0 || value > 1000) {
                    this.showFieldError(field, 'La capacidad debe estar entre 1 y 1000.');
                }
                break;
        }
    }
    
    validateForm(e) {
        this.errors = [];
        
        // Validar todos los campos requeridos
        const requiredFields = this.form.querySelectorAll('[required]');
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                this.showFieldError(field, 'Este campo es obligatorio.');
                this.errors.push(`${field.name} es obligatorio`);
            }
        });
        
        // Validar campos específicos
        const textInputs = this.form.querySelectorAll('input[type="text"], input[type="email"], input[type="password"]');
        textInputs.forEach(input => this.validateField(input));
        
        const dateInputs = this.form.querySelectorAll('input[type="date"]');
        dateInputs.forEach(input => this.validateDate(input));
        
        const numberInputs = this.form.querySelectorAll('input[type="number"]');
        numberInputs.forEach(input => this.validateNumber(input));
        
        // Si hay errores, prevenir el envío
        if (this.errors.length > 0) {
            e.preventDefault();
            this.showFormError('Por favor, corrige los errores antes de continuar.');
            return false;
        }
        
        return true;
    }
    
    showFieldError(field, message) {
        // Crear elemento de error
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        // Añadir clase de error al campo
        field.classList.add('is-invalid');
        
        // Insertar mensaje de error después del campo
        field.parentNode.appendChild(errorDiv);
        
        // Añadir a la lista de errores
        this.errors.push(message);
    }
    
    clearFieldError(field) {
        // Remover clase de error
        field.classList.remove('is-invalid');
        
        // Remover mensaje de error
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
    
    showFormError(message) {
        // Mostrar mensaje de error general
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-danger alert-dismissible fade show';
        alertDiv.innerHTML = `
            <i class="bi bi-exclamation-triangle"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insertar al inicio del formulario
        this.form.insertBefore(alertDiv, this.form.firstChild);
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    isValidDocument(document) {
        // Validación básica de documento (puede ser personalizada por país)
        const docRegex = /^[0-9]{7,12}$/;
        return docRegex.test(document.replace(/\D/g, ''));
    }
    
    isValidPhone(phone) {
        // Validación básica de teléfono
        const phoneRegex = /^[\+]?[0-9\s\-\(\)]{7,15}$/;
        return phoneRegex.test(phone);
    }
}

/**
 * Validaciones específicas para reservas
 */
class ReservationValidator {
    constructor() {
        this.selectedSeats = new Set();
        this.maxPassengers = VALIDATION_CONFIG.maxPassengersPerReservation;
    }
    
    validateSeatSelection(seatElement, vueloId) {
        const seatId = seatElement.dataset.asientoId;
        const seatNumber = seatElement.dataset.asientoNumero;
        
        // Verificar si el asiento ya está seleccionado
        if (this.selectedSeats.has(seatId)) {
            this.showError(`El asiento ${seatNumber} ya está seleccionado.`);
            return false;
        }
        
        // Verificar límite de pasajeros
        if (this.selectedSeats.size >= this.maxPassengers) {
            this.showError(`No puedes seleccionar más de ${this.maxPassengers} asientos.`);
            return false;
        }
        
        // Verificar disponibilidad en tiempo real
        return this.checkSeatAvailability(seatId, vueloId);
    }
    
    async checkSeatAvailability(seatId, vueloId) {
        try {
            const response = await fetch(`/asientos/${seatId}/disponibilidad/?vuelo_id=${vueloId}`);
            const data = await response.json();
            
            if (!data.disponible) {
                this.showError(`El asiento ${data.numero} no está disponible.`);
                return false;
            }
            
            return true;
        } catch (error) {
            console.error('Error verificando disponibilidad:', error);
            this.showError('Error verificando disponibilidad del asiento.');
            return false;
        }
    }
    
    validateFlightDate(flightDate) {
        const selectedDate = new Date(flightDate);
        const today = new Date();
        const minDate = new Date(today.getTime() + (VALIDATION_CONFIG.minReservationHours * 60 * 60 * 1000));
        const maxDate = new Date(today.getTime() + (VALIDATION_CONFIG.maxReservationDays * 24 * 60 * 60 * 1000));
        
        if (selectedDate < minDate) {
            this.showError(`La reserva debe realizarse al menos ${VALIDATION_CONFIG.minReservationHours} horas antes del vuelo.`);
            return false;
        }
        
        if (selectedDate > maxDate) {
            this.showError(`No puedes reservar vuelos con más de ${VALIDATION_CONFIG.maxReservationDays} días de anticipación.`);
            return false;
        }
        
        return true;
    }
    
    showError(message) {
        // Crear notificación de error
        const notification = document.createElement('div');
        notification.className = 'alert alert-danger alert-dismissible fade show position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            <i class="bi bi-exclamation-triangle"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-ocultar después de 5 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

/**
 * Validaciones de búsqueda
 */
class SearchValidator {
    validateFlightSearch(formData) {
        const errors = [];
        
        // Validar que al menos un criterio esté presente
        if (!formData.get('origen') && !formData.get('destino') && !formData.get('fecha_desde')) {
            errors.push('Debes especificar al menos un criterio de búsqueda.');
        }
        
        // Validar fechas
        const fechaDesde = formData.get('fecha_desde');
        const fechaHasta = formData.get('fecha_hasta');
        
        if (fechaDesde && fechaHasta) {
            const desde = new Date(fechaDesde);
            const hasta = new Date(fechaHasta);
            
            if (desde > hasta) {
                errors.push('La fecha de inicio no puede ser posterior a la fecha de fin.');
            }
        }
        
        // Validar precios
        const precioMin = parseFloat(formData.get('precio_min') || 0);
        const precioMax = parseFloat(formData.get('precio_max') || 0);
        
        if (precioMin > 0 && precioMax > 0 && precioMin > precioMax) {
            errors.push('El precio mínimo no puede ser mayor al precio máximo.');
        }
        
        return errors;
    }
}

// Inicializar validadores cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar validadores de formularios
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        new FormValidator(form.id);
    });
    
    // Inicializar validador de reservas
    if (document.querySelector('.asiento')) {
        window.reservationValidator = new ReservationValidator();
    }
    
    // Inicializar validador de búsqueda
    if (document.querySelector('form[data-search]')) {
        window.searchValidator = new SearchValidator();
    }
});

// Exportar para uso en otros módulos
window.FormValidator = FormValidator;
window.ReservationValidator = ReservationValidator;
window.SearchValidator = SearchValidator; 