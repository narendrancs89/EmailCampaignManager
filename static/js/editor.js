document.addEventListener('DOMContentLoaded', function() {
    // Initialize TinyMCE
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
            'removeformat | help',
        menubar: 'file edit view insert format tools table help',
        content_style: 'body { font-family:Helvetica,Arial,sans-serif; font-size:14px }',
        setup: function(editor) {
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
        });
    }

    // Function to update preview pane
    function updatePreview() {
        const previewPane = document.getElementById('preview-pane');
        const previewSubject = document.getElementById('preview-subject');
        const editor = tinymce.get('email-editor');
        
        if (previewPane && editor) {
            // Set the content
            previewPane.innerHTML = editor.getContent();
            
            // Update subject if empty
            if (previewSubject && !previewSubject.textContent) {
                const subjectField = document.getElementById('subject');
                previewSubject.textContent = subjectField.value || 'Email Subject';
            }
        }
    }

    // Template type selection handling
    const templateTypeSelect = document.getElementById('type');
    if (templateTypeSelect) {
        templateTypeSelect.addEventListener('change', function() {
            // Could add special handling based on template type
            const selectedType = this.value;
            console.log('Selected template type:', selectedType);
            
            // You could modify the editor based on the selected type
            // For example, add a tracking pixel for 'open' templates, etc.
        });
    }

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
});
