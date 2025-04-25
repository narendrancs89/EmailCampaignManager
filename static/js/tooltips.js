// Initialize tooltips with best practices content
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips with the data-bs-toggle="tooltip" attribute
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        // Get tooltip type from data attribute
        const tooltipType = tooltipTriggerEl.dataset.tooltipType || 'default';
        
        // Create tooltip with custom classes based on type
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            html: true,
            template: `<div class="tooltip tooltip-marketing-${tooltipType}" role="tooltip">
                        <div class="tooltip-arrow"></div>
                        <div class="tooltip-inner"></div>
                      </div>`
        });
    });
    
    // Helper function to create tooltip icons with content
    window.createTooltip = function(element, content, type = 'best-practice') {
        // Create the tooltip icon
        const tooltipIcon = document.createElement('span');
        tooltipIcon.className = 'tooltip-icon';
        tooltipIcon.innerHTML = '<i class="fas fa-info"></i>';
        tooltipIcon.setAttribute('data-bs-toggle', 'tooltip');
        tooltipIcon.setAttribute('data-bs-html', 'true');
        tooltipIcon.setAttribute('data-bs-placement', 'right');
        tooltipIcon.setAttribute('data-tooltip-type', type);
        tooltipIcon.setAttribute('title', content);
        
        // Append the tooltip icon to the element
        element.appendChild(tooltipIcon);
        
        // Initialize the tooltip
        new bootstrap.Tooltip(tooltipIcon, {
            html: true,
            template: `<div class="tooltip tooltip-marketing-${type}" role="tooltip">
                        <div class="tooltip-arrow"></div>
                        <div class="tooltip-inner"></div>
                      </div>`
        });
    };
    
    // Add tooltips to common email marketing fields throughout the application
    addEmailMarketingTooltips();
});

// Function to add specific tooltips to email marketing related elements
function addEmailMarketingTooltips() {
    // Subject line best practices
    const subjectInputs = document.querySelectorAll('input[name$="subject"]');
    subjectInputs.forEach(input => {
        const label = input.closest('.mb-3').querySelector('label');
        if (label) {
            createTooltip(
                label, 
                `<strong>Subject Line Best Practices:</strong><br>
                • Keep subject lines under 50 characters<br>
                • Avoid spam trigger words like "free" or "discount"<br>
                • Use personalization when possible<br>
                • Create a sense of urgency without being misleading<br>
                • A/B test different subject lines for better results`,
                'best-practice'
            );
        }
    });
    
    // Email sender name best practices
    const fromNameInputs = document.querySelectorAll('input[name$="from_name"]');
    fromNameInputs.forEach(input => {
        const label = input.closest('.mb-3').querySelector('label');
        if (label) {
            createTooltip(
                label, 
                `<strong>Sender Name Best Practices:</strong><br>
                • Use a consistent sender name for brand recognition<br>
                • Company name + individual name performs best (e.g., "Sarah from Acme")<br>
                • Avoid generic names like "Marketing Team" or "No-Reply"<br>
                • Keep it professional but personable`,
                'best-practice'
            );
        }
    });
    
    // Open tracking tips
    const openTrackingCheckboxes = document.querySelectorAll('input[name$="has_open_tracking"]');
    openTrackingCheckboxes.forEach(checkbox => {
        const label = checkbox.closest('.mb-3').querySelector('label');
        if (label) {
            createTooltip(
                label, 
                `<strong>Open Tracking:</strong><br>
                • Tracks when recipients open your email<br>
                • Works by embedding a small transparent tracking pixel<br>
                • May be blocked by some email clients<br>
                • Average open rates across industries: 15-25%<br>
                • Helps measure engagement and timing preferences`,
                'idea'
            );
        }
    });
    
    // Click tracking tips
    const clickTrackingCheckboxes = document.querySelectorAll('input[name$="has_click_tracking"]');
    clickTrackingCheckboxes.forEach(checkbox => {
        const label = checkbox.closest('.mb-3').querySelector('label');
        if (label) {
            createTooltip(
                label, 
                `<strong>Click Tracking:</strong><br>
                • Monitors which links recipients click in your email<br>
                • Works by redirecting links through our tracking system<br>
                • Average click rates: 2.5-5% across industries<br>
                • Click-to-open ratio is a key engagement metric<br>
                • Place important links early in the email for better results`,
                'idea'
            );
        }
    });
    
    // Email content tips (for TinyMCE editor)
    setTimeout(() => {
        const editorContainers = document.querySelectorAll('.tox-tinymce');
        editorContainers.forEach(container => {
            const editorLabel = container.closest('.mb-3')?.querySelector('label');
            if (editorLabel) {
                createTooltip(
                    editorLabel, 
                    `<strong>Email Content Best Practices:</strong><br>
                    • Keep emails concise (50-125 words performs best)<br>
                    • Use a clear call-to-action (CTA) button<br>
                    • Maintain a text-to-image ratio of at least 80:20<br>
                    • Use responsive design that works on mobile<br>
                    • Include ALT text for all images<br>
                    • Test your emails across different clients before sending`,
                    'best-practice'
                );
            }
        });
    }, 1000); // Delay to ensure TinyMCE is loaded
    
    // Segment selection tips
    const segmentSelects = document.querySelectorAll('select[name$="segment_id"]');
    segmentSelects.forEach(select => {
        const label = select.closest('.mb-3').querySelector('label');
        if (label) {
            createTooltip(
                label, 
                `<strong>Audience Segmentation Tips:</strong><br>
                • Targeted segments get 14.31% higher open rates<br>
                • Segment based on behavior, demographics, or preferences<br>
                • Smaller, more targeted segments often outperform larger lists<br>
                • Consider creating segments based on past email engagement<br>
                • Regularly clean your lists to maintain deliverability`,
                'idea'
            );
        }
    });
    
    // Schedule time tips
    const scheduleTimeInputs = document.querySelectorAll('input[name$="scheduled_time"]');
    scheduleTimeInputs.forEach(input => {
        const label = input.closest('.mb-3').querySelector('label');
        if (label) {
            createTooltip(
                label, 
                `<strong>Email Timing Best Practices:</strong><br>
                • Tuesday, Wednesday, and Thursday typically have best open rates<br>
                • 10am-2pm is generally optimal for B2B emails<br>
                • Consider your audience's time zone and habits<br>
                • Avoid sending during major holidays or weekends<br>
                • Maintain consistent sending frequency to meet expectations`,
                'best-practice'
            );
        }
    });
    
    // SMTP configuration warnings
    const smtpHostInputs = document.querySelectorAll('input[name$="host"]');
    smtpHostInputs.forEach(input => {
        const label = input.closest('.mb-3').querySelector('label');
        if (label) {
            createTooltip(
                label, 
                `<strong>SMTP Configuration Warning:</strong><br>
                • Verify your SMTP provider's sending limits<br>
                • Ensure proper SPF, DKIM, and DMARC records are set up<br>
                • Consider using a dedicated IP for large volume sending<br>
                • Monitor your sending reputation regularly<br>
                • Test deliverability before sending to your entire list`,
                'warning'
            );
        }
    });
}