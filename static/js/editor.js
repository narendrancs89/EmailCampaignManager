document.addEventListener('DOMContentLoaded', function() {
    // Check if TinyMCE is defined
    if (typeof tinymce === 'undefined') {
        console.error('TinyMCE is not loaded. Please check the script inclusion.');
        
        // Add a fallback basic editor
        const editorTextarea = document.getElementById('email-editor');
        if (editorTextarea) {
            editorTextarea.style.display = 'block';
            editorTextarea.style.width = '100%';
            editorTextarea.style.minHeight = '400px';
            editorTextarea.addEventListener('input', function() {
                document.getElementById('content').value = this.value;
                document.getElementById('preview-pane').innerHTML = this.value;
            });
            
            // Load any existing content
            const contentField = document.getElementById('content');
            if (contentField && contentField.value) {
                editorTextarea.value = contentField.value;
                document.getElementById('preview-pane').innerHTML = contentField.value;
            }
        }
        
        // Initialize tracking options UI
        initTrackingOptions();
        
        return;
    }
    
    // Initialize TinyMCE if it's available
    tinymce.init({
        selector: '#email-editor',
        height: 500,
        plugins: [
            'advlist autolink lists link image charmap print preview anchor',
            'searchreplace visualblocks code fullscreen',
            'insertdatetime media table paste code help wordcount'
        ],
        toolbar: 'undo redo | formatselect | ' +
            'bold italic backcolor | alignleft aligncenter ' +
            'alignright alignjustify | bullist numlist outdent indent | ' +
            'link image | removeformat | code',
        menubar: 'file edit view insert format tools table help',
        content_style: `
            body { 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; 
                font-size: 14px; 
                line-height: 1.5;
                color: #333;
                max-width: 100%;
                margin: 0;
                padding: 0;
            }
            table { width: 100%; border-collapse: collapse; }
            img { max-width: 100%; height: auto; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            h1, h2, h3, h4, h5, h6 { margin-top: 0; margin-bottom: 0.5rem; }
            p { margin-top: 0; margin-bottom: 1rem; }
        `,
        // Enable file picker for images
        file_picker_types: 'image',
        // Setup image upload
        images_upload_handler: function (blobInfo, success, failure) {
            // For demonstration purposes, we'll use a placeholder image
            // In a production environment, you would upload to a server
            const imageUrl = 'https://via.placeholder.com/800x400';
            success(imageUrl);
        },
        setup: function(editor) {
            // Register custom buttons
            editor.ui.registry.addButton('insertVariable', {
                text: 'Insert Variable',
                tooltip: 'Insert personalization variable',
                onAction: function() {
                    editor.windowManager.open({
                        title: 'Insert Personalization Variable',
                        body: {
                            type: 'panel',
                            items: [
                                {
                                    type: 'selectbox',
                                    name: 'variable',
                                    label: 'Select Variable',
                                    items: [
                                        {text: 'Recipient Name', value: '{{name}}'},
                                        {text: 'Recipient Email', value: '{{email}}'},
                                        {text: 'Company Name', value: '{{company}}'},
                                        {text: 'Unsubscribe Link', value: '{{unsubscribe}}'}
                                    ]
                                }
                            ]
                        },
                        buttons: [
                            {
                                text: 'Insert',
                                primary: true,
                                onAction: function(api) {
                                    const data = api.getData();
                                    editor.insertContent(data.variable);
                                    api.close();
                                }
                            },
                            {
                                text: 'Close',
                                onAction: function(api) {
                                    api.close();
                                }
                            }
                        ],
                        width: 400
                    });
                }
            });
            
            // Change events
            editor.on('change', function() {
                updatePreview();
                // Update hidden form field
                document.getElementById('content').value = editor.getContent();
            });
            
            // Initial setup for editor when loaded
            editor.on('init', function() {
                // Get content from hidden field if editing an existing template
                const contentField = document.getElementById('content');
                if (contentField.value) {
                    editor.setContent(contentField.value);
                }
                updatePreview();
            });
        }
    });

    // Update preview when subject changes
    const subjectField = document.getElementById('subject');
    if (subjectField) {
        subjectField.addEventListener('input', function() {
            const previewSubject = document.getElementById('preview-subject');
            if (previewSubject) {
                previewSubject.textContent = this.value || 'Email Subject';
            }
            updatePreview();
        });
    }

    // Initialize tracking options
    initTrackingOptions();

    // Initialize responsive preview
    initDevicePreview();
    
    // Initialize template blocks
    initTemplateBlocks();
    
    // Initialize variable insertion
    initVariableInsertion();
    
    // Initialize preview options
    initPreviewOptions();
    
    // Form submission handling
    const emailForm = document.getElementById('email-form');
    if (emailForm) {
        emailForm.addEventListener('submit', function(e) {
            // Ensure content field is updated with latest editor content
            const editor = tinymce.get('email-editor');
            const contentField = document.getElementById('content');
            
            if (editor && contentField) {
                contentField.value = editor.getContent();
            }
            
            // Validate form
            if (!contentField.value.trim()) {
                e.preventDefault();
                alert('Please add content to your email before saving.');
                return false;
            }
        });
    }
    
    // Function to update preview pane
    function updatePreview(options = {}) {
        const previewPane = document.getElementById('preview-pane');
        const previewSubject = document.getElementById('preview-subject');
        
        // Get content from TinyMCE if available, otherwise from textarea
        let editor = null;
        let content = '';
        
        if (typeof tinymce !== 'undefined') {
            editor = tinymce.get('email-editor');
            if (editor) {
                content = editor.getContent();
            }
        }
        
        // Fallback to textarea if TinyMCE is not available or initialized
        if (!editor) {
            const editorTextarea = document.getElementById('email-editor');
            if (editorTextarea) {
                content = editorTextarea.value;
            }
        }
        
        if (previewPane) {
            // Apply personalization if requested
            if (options.personalize) {
                content = applyPersonalization(content, options.personalizationData);
            }
            
            // Add tracking markers if requested
            if (options.showTracking) {
                content = addTrackingMarkers(content);
            }
            
            // Set the content
            previewPane.innerHTML = content;
            
            // Update subject if needed
            if (previewSubject && !previewSubject.textContent) {
                const subjectField = document.getElementById('subject');
                previewSubject.textContent = subjectField.value || 'Email Subject';
            }
        }
    }
    
    // Function to add tracking markers to the preview
    function addTrackingMarkers(content, templateType) {
        let modifiedContent = content;
        
        // Get tracking options checkboxes
        const hasClickTracking = document.getElementById('has_click_tracking') && 
                               document.getElementById('has_click_tracking').checked;
        const hasOpenTracking = document.getElementById('has_open_tracking') && 
                              document.getElementById('has_open_tracking').checked;
        const hasOptout = document.getElementById('has_optout') && 
                        document.getElementById('has_optout').checked;
        
        // Get tracking URLs
        const clickTrackingUrl = document.getElementById('click_tracking_url') ? 
                               document.getElementById('click_tracking_url').value : null;
        const openTrackingUrl = document.getElementById('open_tracking_url') ? 
                              document.getElementById('open_tracking_url').value : null;
        const trackingImageUrl = document.getElementById('tracking_image_url') ? 
                               document.getElementById('tracking_image_url').value : null;
        const optoutUrl = document.getElementById('optout_url') ? 
                        document.getElementById('optout_url').value : null;
        
        // Add open tracking indicator
        if (hasOpenTracking) {
            const pixelUrl = trackingImageUrl || 'https://via.placeholder.com/1x1.png';
            const trackingUrl = openTrackingUrl || '#';
            
            modifiedContent += `
                <div class="tracking-marker open-tracker">
                    <i class="fas fa-eye me-1"></i> <strong>Open Tracking:</strong> 
                    <span>A tracking pixel will be inserted in your email to track opens.</span>
                    ${openTrackingUrl ? 
                        `<div><strong>Tracking URL:</strong> <code>${trackingUrl}?recipient={{email}}</code></div>` : 
                        '<div><strong>Warning:</strong> Please provide a tracking URL.</div>'}
                    ${trackingImageUrl ? 
                        `<div><strong>Pixel Image:</strong> <code>${pixelUrl}</code></div>` : 
                        ''}
                </div>
            `;
        }
        
        // Add click tracking indicators to all links
        if (hasClickTracking) {
            // Create a temporary element to parse the HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = modifiedContent;
            
            // Find all links and add tracking indicators
            const links = tempDiv.querySelectorAll('a');
            if (links.length > 0) {
                links.forEach(link => {
                    const originalUrl = link.getAttribute('href');
                    if (originalUrl && !originalUrl.startsWith('#') && !originalUrl.startsWith('mailto:')) {
                        // Create tracking indicator
                        const trackingMarker = document.createElement('div');
                        trackingMarker.className = 'tracking-marker click-tracker';
                        const trackingUrl = clickTrackingUrl || '#';
                        
                        trackingMarker.innerHTML = `
                            <i class="fas fa-link me-1"></i> <strong>Click Tracking:</strong>
                            <span>This link will be modified for click tracking.</span>
                            ${clickTrackingUrl ? 
                                `<div><strong>From:</strong> <code>${originalUrl}</code></div>
                                <div><strong>To:</strong> <code>${trackingUrl}?url=${encodeURIComponent(originalUrl)}&recipient={{email}}</code></div>` :
                                '<div><strong>Warning:</strong> Please provide a tracking URL.</div>'}
                        `;
                        
                        // Insert the tracking marker after the link
                        link.parentNode.insertBefore(trackingMarker, link.nextSibling);
                    }
                });
            } else {
                // No links found, add a general message
                modifiedContent += `
                    <div class="tracking-marker click-tracker">
                        <i class="fas fa-link me-1"></i> <strong>Click Tracking:</strong>
                        <span>No links found in your email. Add links to enable click tracking.</span>
                        ${clickTrackingUrl ? 
                            `<div><strong>Tracking URL:</strong> <code>${clickTrackingUrl}?url=[original-url]&recipient={{email}}</code></div>` : 
                            '<div><strong>Warning:</strong> Please provide a tracking URL.</div>'}
                    </div>
                `;
            }
            
            if (links.length > 0) {
                modifiedContent = tempDiv.innerHTML;
            }
        }
        
        // Add opt-out section for opt-out templates
        if (hasOptout) {
            const unsubscribeUrl = optoutUrl || '#';
            
            modifiedContent += `
                <div class="tracking-marker optout-section">
                    <i class="fas fa-ban me-1"></i> <strong>Unsubscribe Footer:</strong>
                    <span>An unsubscribe link will be added to the bottom of your email.</span>
                    ${optoutUrl ? 
                        `<div><strong>Unsubscribe URL:</strong> <code>${unsubscribeUrl}?email={{email}}</code></div>` : 
                        '<div><strong>Warning:</strong> Please provide an unsubscribe URL.</div>'}
                </div>
            `;
        }
        
        return modifiedContent;
    }
    
    // Function to apply personalization in preview
    function applyPersonalization(content, data) {
        let personalizedContent = content;
        
        // Replace name variable
        if (data.name) {
            personalizedContent = personalizedContent.replace(/{{name}}/g, data.name);
        }
        
        // Replace email variable
        if (data.email) {
            personalizedContent = personalizedContent.replace(/{{email}}/g, data.email);
        }
        
        // Replace company variable
        if (data.company) {
            personalizedContent = personalizedContent.replace(/{{company}}/g, data.company);
        }
        
        // Replace unsubscribe link
        personalizedContent = personalizedContent.replace(/{{unsubscribe}}/g, '<a href="#unsubscribe">Unsubscribe</a>');
        
        return personalizedContent;
    }
    
    // Initialize tracking options functionality
    function initTrackingOptions() {
        // Get checkbox elements
        const clickTrackingCheckbox = document.getElementById('has_click_tracking');
        const openTrackingCheckbox = document.getElementById('has_open_tracking');
        const optoutCheckbox = document.getElementById('has_optout');
        
        // Get URL input elements
        const clickTrackingUrl = document.getElementById('click_tracking_url');
        const openTrackingUrl = document.getElementById('open_tracking_url');
        const trackingImageUrl = document.getElementById('tracking_image_url');
        const optoutUrl = document.getElementById('optout_url');
        
        // Get options containers
        const clickTrackingOptions = document.getElementById('click_tracking_options');
        const openTrackingOptions = document.getElementById('open_tracking_options');
        const optoutOptions = document.getElementById('optout_options');
        
        // Type hidden field for backward compatibility
        const typeField = document.getElementById('type');
        
        // Function to update the type field value based on checkboxes
        function updateTypeField() {
            const types = [];
            
            if (clickTrackingCheckbox && clickTrackingCheckbox.checked) {
                types.push('click');
            }
            
            if (openTrackingCheckbox && openTrackingCheckbox.checked) {
                types.push('open');
            }
            
            if (optoutCheckbox && optoutCheckbox.checked) {
                types.push('optout');
            }
            
            // Set the type field value as comma-separated string
            if (typeField) {
                typeField.value = types.join(',');
            }
            
            // Update preview to show tracking markers
            updatePreview({ showTracking: true });
        }
        
        // Function to handle tracking checkbox changes
        function handleTrackingCheckboxChange(checkbox, optionsContainer) {
            if (checkbox && optionsContainer) {
                // Initialize visibility based on initial checkbox state
                optionsContainer.style.display = checkbox.checked ? 'block' : 'none';
                
                // Handle checkbox changes
                checkbox.addEventListener('change', function() {
                    optionsContainer.style.display = this.checked ? 'block' : 'none';
                    updateTypeField();
                });
            }
        }
        
        // Initialize visibility for each tracking option
        handleTrackingCheckboxChange(clickTrackingCheckbox, clickTrackingOptions);
        handleTrackingCheckboxChange(openTrackingCheckbox, openTrackingOptions);
        handleTrackingCheckboxChange(optoutCheckbox, optoutOptions);
        
        // Add URL change handlers to update preview
        const urlInputs = [clickTrackingUrl, openTrackingUrl, trackingImageUrl, optoutUrl];
        urlInputs.forEach(input => {
            if (input) {
                input.addEventListener('input', function() {
                    // Update preview when URL changes
                    updatePreview({ showTracking: true });
                });
            }
        });
        
        // Set initial type field value
        updateTypeField();
        
        // Add URL generation functions
        function generateTrackingContent() {
            const editor = typeof tinymce !== 'undefined' ? tinymce.get('email-editor') : null;
            const contentField = document.getElementById('content');
            let content = editor ? editor.getContent() : (contentField ? contentField.value : '');
            
            // Process content based on enabled tracking options
            if (clickTrackingCheckbox && clickTrackingCheckbox.checked && clickTrackingUrl && clickTrackingUrl.value) {
                content = addClickTracking(content, clickTrackingUrl.value);
            }
            
            if (openTrackingCheckbox && openTrackingCheckbox.checked) {
                if (openTrackingUrl && openTrackingUrl.value) {
                    const pixelUrl = trackingImageUrl && trackingImageUrl.value ? 
                        trackingImageUrl.value : 
                        'https://via.placeholder.com/1x1.png?text=.';
                    
                    content = addOpenTracking(content, openTrackingUrl.value, pixelUrl);
                }
            }
            
            if (optoutCheckbox && optoutCheckbox.checked && optoutUrl && optoutUrl.value) {
                content = addOptoutFooter(content, optoutUrl.value);
            }
            
            return content;
        }
        
        // Add click tracking to all links
        function addClickTracking(content, trackingUrl) {
            // Parse the HTML
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = content;
            
            // Find all links
            const links = tempDiv.querySelectorAll('a');
            links.forEach(link => {
                const originalUrl = link.getAttribute('href');
                if (originalUrl && !originalUrl.startsWith('#') && !originalUrl.startsWith('mailto:')) {
                    // Create tracking URL
                    const trackingRedirectUrl = `${trackingUrl}?url=${encodeURIComponent(originalUrl)}&recipient={{email}}`;
                    link.setAttribute('href', trackingRedirectUrl);
                    link.setAttribute('data-original-url', originalUrl);
                    link.setAttribute('title', `${link.getAttribute('title') || ''} (Tracked)`.trim());
                }
            });
            
            return tempDiv.innerHTML;
        }
        
        // Add open tracking pixel
        function addOpenTracking(content, trackingUrl, pixelUrl) {
            // Create tracking pixel
            const trackingPixel = `<img src="${pixelUrl}" alt="" width="1" height="1" style="display:none" data-tracking-url="${trackingUrl}?recipient={{email}}" />`;
            
            // Add the pixel at the end of the email
            return `${content}\n${trackingPixel}`;
        }
        
        // Add unsubscribe footer
        function addOptoutFooter(content, optoutUrl) {
            // Create unsubscribe footer
            const optoutFooter = `
                <div style="border-top: 1px solid #ddd; margin-top: 20px; padding-top: 10px; color: #666; font-size: 12px; text-align: center;">
                    <p>If you no longer wish to receive emails from us, you can <a href="${optoutUrl}?email={{email}}" style="color: #666;">unsubscribe here</a>.</p>
                </div>
            `;
            
            // Add the footer at the end of the email
            return `${content}\n${optoutFooter}`;
        }
        
        // Handle form submission to process the content with tracking elements
        const emailForm = document.getElementById('email-form');
        if (emailForm) {
            emailForm.addEventListener('submit', function(e) {
                const contentField = document.getElementById('content');
                
                // Generate final content with tracking elements
                const finalContent = generateTrackingContent();
                
                // Set the final content to the hidden field
                if (contentField) {
                    contentField.value = finalContent;
                }
            });
        }
    }
    
    // Initialize device preview functionality
    function initDevicePreview() {
        const deviceButtons = document.querySelectorAll('.preview-device-toolbar button');
        const previewPane = document.getElementById('preview-pane');
        
        deviceButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons
                deviceButtons.forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                this.classList.add('active');
                
                // Get the device type
                const deviceType = this.getAttribute('data-device');
                
                // Remove all device classes from preview pane
                previewPane.classList.remove('preview-mobile', 'preview-tablet');
                
                // Add appropriate class based on device type
                if (deviceType === 'mobile') {
                    previewPane.classList.add('preview-mobile');
                } else if (deviceType === 'tablet') {
                    previewPane.classList.add('preview-tablet');
                }
                
                // Update preview
                updatePreview();
            });
        });
    }
    
    // Initialize template blocks functionality
    function initTemplateBlocks() {
        const insertTemplateBtn = document.getElementById('insert-template-btn');
        const templateBlocks = document.querySelectorAll('.template-block');
        
        if (insertTemplateBtn) {
            insertTemplateBtn.addEventListener('click', function() {
                // Show the template blocks modal
                const modal = new bootstrap.Modal(document.getElementById('template-blocks-modal'));
                modal.show();
            });
        }
        
        // Handle template block selection
        templateBlocks.forEach(block => {
            block.addEventListener('click', function() {
                const templateType = this.getAttribute('data-template');
                const editor = tinymce.get('email-editor');
                
                if (editor) {
                    let templateHtml = '';
                    
                    // Generate appropriate HTML based on template type
                    switch (templateType) {
                        case 'header':
                            templateHtml = `
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8f9fa; padding: 20px;">
                                    <tr>
                                        <td align="center">
                                            <img src="https://via.placeholder.com/200x60" alt="Company Logo" style="margin-bottom: 10px;">
                                            <h2 style="color: #333; margin: 0;">Company Name</h2>
                                        </td>
                                    </tr>
                                </table>
                            `;
                            break;
                        case 'hero':
                            templateHtml = `
                                <table width="100%" border="0" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td align="center" style="padding: 40px 20px; background-color: #007bff; color: white;">
                                            <h1 style="margin: 0 0 20px 0;">Main Headline Here</h1>
                                            <p style="margin: 0 0 30px 0;">Subheadline or brief description goes here.</p>
                                            <a href="#" style="background-color: #ffffff; color: #007bff; padding: 12px 25px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">Call to Action</a>
                                        </td>
                                    </tr>
                                </table>
                            `;
                            break;
                        case 'text':
                            templateHtml = `
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="padding: 20px;">
                                    <tr>
                                        <td>
                                            <h2 style="color: #333; margin-bottom: 15px;">Section Headline</h2>
                                            <p style="margin-bottom: 15px;">Lorem ipsum dolor sit amet, consectetur adipiscing elit. Suspendisse quis neque in mauris auctor venenatis sed eget libero. Sed lacinia nunc eget mi sagittis, et elementum magna posuere.</p>
                                            <p>Donec finibus hendrerit dolor, nec semper nisi auctor sed. Morbi nec magna eleifend, bibendum lorem vitae, rutrum neque.</p>
                                        </td>
                                    </tr>
                                </table>
                            `;
                            break;
                        case 'button':
                            templateHtml = `
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="padding: 30px 20px;">
                                    <tr>
                                        <td align="center">
                                            <a href="#" style="background-color: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">Click Here</a>
                                        </td>
                                    </tr>
                                </table>
                            `;
                            break;
                        case 'columns':
                            templateHtml = `
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="padding: 20px;">
                                    <tr>
                                        <td width="50%" style="padding-right: 10px; vertical-align: top;">
                                            <h3 style="color: #333;">Left Column</h3>
                                            <p>Content for the left column goes here. You can add text, images, or any other elements.</p>
                                        </td>
                                        <td width="50%" style="padding-left: 10px; vertical-align: top;">
                                            <h3 style="color: #333;">Right Column</h3>
                                            <p>Content for the right column goes here. You can add text, images, or any other elements.</p>
                                        </td>
                                    </tr>
                                </table>
                            `;
                            break;
                        case 'footer':
                            templateHtml = `
                                <table width="100%" border="0" cellspacing="0" cellpadding="0" style="background-color: #f8f9fa; padding: 20px; margin-top: 20px;">
                                    <tr>
                                        <td align="center">
                                            <p style="margin-bottom: 10px;">© 2025 Your Company. All rights reserved.</p>
                                            <p style="color: #6c757d; font-size: 12px;">
                                                You're receiving this email because you signed up for updates from our company.
                                                <br>
                                                <a href="{{unsubscribe}}" style="color: #6c757d;">Unsubscribe</a>
                                            </p>
                                        </td>
                                    </tr>
                                </table>
                            `;
                            break;
                    }
                    
                    // Insert the template HTML
                    editor.insertContent(templateHtml);
                    
                    // Close the modal
                    const modal = bootstrap.Modal.getInstance(document.getElementById('template-blocks-modal'));
                    if (modal) {
                        modal.hide();
                    }
                    
                    // Update preview
                    updatePreview();
                }
            });
        });
    }
    
    // Initialize variable insertion functionality
    function initVariableInsertion() {
        const variableCodes = document.querySelectorAll('.personalization-variables code');
        
        variableCodes.forEach(code => {
            code.addEventListener('click', function() {
                const variableText = this.getAttribute('data-variable');
                const editor = tinymce.get('email-editor');
                
                if (editor && variableText) {
                    editor.insertContent(variableText);
                    editor.focus();
                }
            });
        });
    }
    
    // Initialize preview options
    function initPreviewOptions() {
        // Toggle HTML view
        const toggleHtmlBtn = document.getElementById('toggle-html-btn');
        if (toggleHtmlBtn) {
            toggleHtmlBtn.addEventListener('click', function() {
                const editor = tinymce.get('email-editor');
                if (editor) {
                    if (editor.plugins.code) {
                        editor.execCommand('mceCodeEditor');
                    }
                }
            });
        }
        
        // Show tracking elements button
        const showTrackingBtn = document.getElementById('show-tracking-btn');
        if (showTrackingBtn) {
            showTrackingBtn.addEventListener('click', function(e) {
                e.preventDefault();
                updatePreview({ showTracking: true });
            });
        }
        
        // Test personalization button
        const testPersonalizationBtn = document.getElementById('test-personalization-btn');
        if (testPersonalizationBtn) {
            testPersonalizationBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Show the personalization modal
                const modal = new bootstrap.Modal(document.getElementById('test-personalization-modal'));
                modal.show();
            });
        }
        
        // Apply personalization button
        const applyPersonalizationBtn = document.getElementById('apply-personalization-btn');
        if (applyPersonalizationBtn) {
            applyPersonalizationBtn.addEventListener('click', function() {
                const nameInput = document.getElementById('test-name');
                const emailInput = document.getElementById('test-email');
                const companyInput = document.getElementById('test-company');
                
                // Get test data
                const personalizationData = {
                    name: nameInput ? nameInput.value : 'John Doe',
                    email: emailInput ? emailInput.value : 'john@example.com',
                    company: companyInput ? companyInput.value : 'ACME Inc.'
                };
                
                // Update the preview with personalization
                updatePreview({
                    personalize: true,
                    personalizationData: personalizationData
                });
                
                // Close the modal
                const modal = bootstrap.Modal.getInstance(document.getElementById('test-personalization-modal'));
                if (modal) {
                    modal.hide();
                }
            });
        }
        
        // Send test email button
        const sendTestEmailBtn = document.getElementById('send-test-email-btn');
        if (sendTestEmailBtn) {
            sendTestEmailBtn.addEventListener('click', function(e) {
                e.preventDefault();
                
                const editor = tinymce.get('email-editor');
                const subjectField = document.getElementById('subject');
                
                if (editor && subjectField && subjectField.value) {
                    // In a real implementation, you would send an AJAX request to the server
                    // to send a test email with the current template
                    alert('This would send a test email with the current template. Feature not implemented in this demo.');
                } else {
                    alert('Please provide a subject and content for your email before sending a test.');
                }
            });
        }
    }
});
