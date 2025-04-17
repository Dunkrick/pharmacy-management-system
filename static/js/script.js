// script.js - Main JavaScript file for Pharmacy Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap components
    initializeBootstrapComponents();
    
    // Setup form validation
    setupFormValidation();
    
    // Setup auto-hiding alerts
    setupAutoHidingAlerts();
    
    // Setup delete confirmations
    setupDeleteConfirmations();
    
    // Setup number formatting
    setupNumberFormatting();
    
    // Setup medicine search
    setupMedicineSearch();
    
    // Setup date inputs
    setupDateInputs();
});

function initializeBootstrapComponents() {
    // Initialize tooltips
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.forEach(function (tooltipTriggerEl) {
            new bootstrap.Tooltip(tooltipTriggerEl);
        });

        // Initialize popovers
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        popoverTriggerList.forEach(function (popoverTriggerEl) {
            new bootstrap.Popover(popoverTriggerEl);
        });
    }
}

function setupFormValidation() {
    // Add custom validation styles
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Add custom validation for phone numbers
    var phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(function(input) {
        input.addEventListener('input', function() {
            var cleaned = this.value.replace(/\D/g, '');
            if (cleaned.length >= 10) {
                this.setCustomValidity('');
            } else {
                this.setCustomValidity('Please enter a valid phone number');
            }
        });
    });
}

function setupAutoHidingAlerts() {
    // Auto-hide alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            } else {
                alert.style.transition = 'opacity 0.5s ease-in-out';
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.remove();
                }, 500);
            }
        }, 5000);
    });
}

function setupDeleteConfirmations() {
    // Add confirmation for delete actions
    var deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(e) {
            if (!confirm(this.dataset.confirm || 'Are you sure you want to delete this item?')) {
                e.preventDefault();
            }
        });
    });
}

function setupNumberFormatting() {
    // Format currency inputs
    var currencyInputs = document.querySelectorAll('input[data-type="currency"]');
    currencyInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            var value = parseFloat(this.value);
            if (!isNaN(value)) {
                this.value = value.toFixed(2);
            }
        });
    });

    // Format quantity inputs
    var quantityInputs = document.querySelectorAll('input[data-type="quantity"]');
    quantityInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            var value = parseInt(this.value);
            if (!isNaN(value)) {
                this.value = Math.max(0, value);
            }
        });
    });

    // Handle medicine price formatting
    var priceInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
    priceInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            this.value = parseFloat(this.value).toFixed(2);
        });
    });

    // Handle stock quantity warnings
    var stockElements = document.querySelectorAll('.stock-quantity');
    stockElements.forEach(function(element) {
        var quantity = parseInt(element.dataset.quantity);
        var reorderLevel = parseInt(element.dataset.reorderLevel);
        
        if (quantity <= reorderLevel) {
            element.classList.add('text-danger', 'fw-bold');
        } else if (quantity <= reorderLevel * 2) {
            element.classList.add('text-warning');
        }
    });
}

function setupMedicineSearch() {
    // Dynamic form handling for medicine search
    var searchForm = document.querySelector('#medicine-search-form');
    if (searchForm) {
        var categorySelect = searchForm.querySelector('select[name="category"]');
        if (categorySelect) {
            categorySelect.addEventListener('change', function() {
                searchForm.submit();
            });
        }
    }

    // Dynamic search suggestions
    var searchInput = document.querySelector('.search-medicine');
    if (searchInput) {
        var debounceTimeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(debounceTimeout);
            debounceTimeout = setTimeout(function() {
                var searchTerm = searchInput.value;
                if (searchTerm.length >= 2) {
                    fetch(`/api/medicines/search?term=${encodeURIComponent(searchTerm)}`)
                        .then(response => response.json())
                        .then(data => {
                            updateSearchSuggestions(data);
                        })
                        .catch(error => console.error('Error:', error));
                }
            }, 300);
        });
    }
}

function setupDateInputs() {
    var dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(function(input) {
        // Set default value to today if no value is set
        if (!input.value) {
            var today = new Date().toISOString().split('T')[0];
            input.value = today;
        }
    });
}

// Utility function to format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Utility function to format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(new Date(date));
}

// Update medicine price in sale form
function updateMedicinePrice(selectElement) {
    var medicineId = selectElement.value;
    if (medicineId) {
        fetch(`/api/medicines/${medicineId}/price`)
            .then(response => response.json())
            .then(data => {
                var priceInput = document.querySelector('#price');
                if (priceInput && data.price) {
                    priceInput.value = data.price;
                    updateTotal();
                }
            })
            .catch(error => console.error('Error:', error));
    }
}

// Calculate total in sale form
function updateTotal() {
    var quantity = parseFloat(document.querySelector('#quantity').value) || 0;
    var price = parseFloat(document.querySelector('#price').value) || 0;
    var totalElement = document.querySelector('#total');
    if (totalElement) {
        totalElement.textContent = (quantity * price).toFixed(2);
    }
}

// Function to update search suggestions
function updateSearchSuggestions(data) {
    var suggestionContainer = document.querySelector('#search-suggestions');
    if (!suggestionContainer) {
        suggestionContainer = document.createElement('div');
        suggestionContainer.id = 'search-suggestions';
        suggestionContainer.className = 'search-suggestions';
        document.querySelector('.search-medicine').parentNode.appendChild(suggestionContainer);
    }
    
    suggestionContainer.innerHTML = '';
    if (data && data.length > 0) {
        data.forEach(function(item) {
            var div = document.createElement('div');
            div.className = 'suggestion-item';
            div.textContent = item.name;
            div.addEventListener('click', function() {
                document.querySelector('.search-medicine').value = item.name;
                suggestionContainer.innerHTML = '';
            });
            suggestionContainer.appendChild(div);
        });
    }
}