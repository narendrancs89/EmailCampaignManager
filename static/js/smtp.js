document.addEventListener('DOMContentLoaded', function() {
    // Toggle password visibility
    const togglePasswordBtn = document.getElementById('toggle-password');
    if (togglePasswordBtn) {
        togglePasswordBtn.addEventListener('click', function() {
            const passwordField = document.getElementById('password');
            const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordField.setAttribute('type', type);
            
            // Update button text
            this.textContent = type === 'password' ? 'Show Password' : 'Hide Password';
        });
    }
    
    // Handle SMTP configuration form
    const smtpForm = document.getElementById('smtp-form');
    if (smtpForm) {
        // Update port based on TLS/SSL selection
        const tlsCheckbox = document.getElementById('use_tls');
        const sslCheckbox = document.getElementById('use_ssl');
        const portField = document.getElementById('port');
        
        if (tlsCheckbox && sslCheckbox && portField) {
            // Function to update port suggestion
            function updatePortSuggestion() {
                if (sslCheckbox.checked) {
                    portField.placeholder = "465 (Default for SSL)";
                    if (!portField.value) {
                        portField.value = "465";
                    }
                } else if (tlsCheckbox.checked) {
                    portField.placeholder = "587 (Default for TLS)";
                    if (!portField.value) {
                        portField.value = "587";
                    }
                } else {
                    portField.placeholder = "25 (Default without encryption)";
                    if (!portField.value) {
                        portField.value = "25";
                    }
                }
            }
            
            // Initial update
            updatePortSuggestion();
            
            // Listen for changes
            tlsCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    sslCheckbox.checked = false;
                }
                updatePortSuggestion();
            });
            
            sslCheckbox.addEventListener('change', function() {
                if (this.checked) {
                    tlsCheckbox.checked = false;
                }
                updatePortSuggestion();
            });
        }
        
        // Test SMTP connection
        const testButton = document.getElementById('test-smtp');
        if (testButton) {
            testButton.addEventListener('click', function(e) {
                e.preventDefault();
                
                const host = document.getElementById('host').value;
                const port = document.getElementById('port').value;
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;
                
                if (!host || !port || !username || !password) {
                    alert('Please fill in all required SMTP fields before testing.');
                    return;
                }
                
                // Get config ID if editing
                const configId = this.dataset.configId;
                if (!configId) {
                    alert('Please save the configuration first before testing.');
                    return;
                }
                
                // Show loading state
                const originalText = this.textContent;
                this.textContent = 'Testing...';
                this.disabled = true;
                
                // Send test request
                fetch(`/smtp-config/${configId}/test`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert('SMTP test successful! Connection established.');
                    } else {
                        alert(`SMTP test failed: ${data.message}`);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert(`SMTP test failed: ${error.message || 'Unknown error'}`);
                })
                .finally(() => {
                    // Restore button state
                    this.textContent = originalText;
                    this.disabled = false;
                });
            });
        }
    }
});
