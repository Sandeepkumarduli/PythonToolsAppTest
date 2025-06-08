/**
 * Main JavaScript file for Tools Website
 * Handles common functionality across all pages
 */

// Global utility functions
const Utils = {
    // Show loading state
    showLoading: (element, text = 'Processing...') => {
        const originalContent = element.innerHTML;
        element.dataset.originalContent = originalContent;
        element.innerHTML = `
            <span class="loading-spinner me-2"></span>
            ${text}
        `;
        element.disabled = true;
    },

    // Hide loading state
    hideLoading: (element) => {
        if (element.dataset.originalContent) {
            element.innerHTML = element.dataset.originalContent;
            delete element.dataset.originalContent;
        }
        element.disabled = false;
    },

    // Show alert message
    showAlert: (container, message, type = 'info') => {
        const alertHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;
        container.innerHTML = alertHTML;
        
        // Auto-hide success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                const alert = container.querySelector('.alert');
                if (alert) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);
        }
    },

    // Format file size
    formatFileSize: (bytes) => {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },

    // Validate file type
    validateFileType: (file, allowedTypes) => {
        const fileExtension = file.name.split('.').pop().toLowerCase();
        return allowedTypes.includes(fileExtension);
    },

    // Validate file size (max 50MB)
    validateFileSize: (file, maxSize = 50 * 1024 * 1024) => {
        return file.size <= maxSize;
    }
};

// File upload handler class
class FileUploader {
    constructor(uploadArea, fileInput, allowedTypes, onFileSelect) {
        this.uploadArea = uploadArea;
        this.fileInput = fileInput;
        this.allowedTypes = allowedTypes;
        this.onFileSelect = onFileSelect;
        this.selectedFile = null;

        this.init();
    }

    init() {
        // Click to upload
        this.uploadArea.addEventListener('click', () => {
            this.fileInput.click();
        });

        // File input change
        this.fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFile(e.target.files[0]);
            }
        });

        // Drag and drop
        this.uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.uploadArea.classList.add('dragover');
        });

        this.uploadArea.addEventListener('dragleave', () => {
            this.uploadArea.classList.remove('dragover');
        });

        this.uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            this.uploadArea.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFile(files[0]);
            }
        });
    }

    handleFile(file) {
        // Validate file type
        if (!Utils.validateFileType(file, this.allowedTypes)) {
            const allowedStr = this.allowedTypes.map(type => type.toUpperCase()).join(', ');
            alert(`Invalid file type. Please select a ${allowedStr} file.`);
            return;
        }

        // Validate file size
        if (!Utils.validateFileSize(file)) {
            alert('File is too large. Maximum size is 50MB.');
            return;
        }

        this.selectedFile = file;
        this.updateUI();
        
        if (this.onFileSelect) {
            this.onFileSelect(file);
        }
    }

    updateUI() {
        if (this.selectedFile) {
            const fileInfo = `
                <div class="file-info">
                    <h5><i class="fas fa-file me-2"></i>${this.selectedFile.name}</h5>
                    <p class="mb-0">Size: ${Utils.formatFileSize(this.selectedFile.size)}</p>
                </div>
            `;
            
            // Update upload area content
            this.uploadArea.innerHTML = fileInfo;
            this.uploadArea.style.cursor = 'default';
        }
    }

    reset() {
        this.selectedFile = null;
        this.fileInput.value = '';
        
        // Reset upload area to original state
        const allowedStr = this.allowedTypes.map(type => type.toUpperCase()).join(', ');
        this.uploadArea.innerHTML = `
            <div class="upload-icon">
                <i class="fas fa-cloud-upload-alt"></i>
            </div>
            <h4>Drop your ${allowedStr} file here</h4>
            <p>or click to browse</p>
            <small class="text-muted">Maximum file size: 50MB</small>
        `;
        this.uploadArea.style.cursor = 'pointer';
    }
}

// API client for making requests
class ApiClient {
    static async convertFile(endpoint, file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Conversion failed');
            }

            return result;
        } catch (error) {
            throw new Error(error.message || 'Network error occurred');
        }
    }

    static async countWords(text) {
        try {
            const response = await fetch('/api/word-count', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ text })
            });

            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.error || 'Word counting failed');
            }

            return result;
        } catch (error) {
            throw new Error(error.message || 'Network error occurred');
        }
    }
}

// Download handler
class DownloadHandler {
    static downloadFile(url, filename) {
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
}

// Initialize common functionality when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scrolling to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add hover effects to cards
    document.querySelectorAll('.tool-card, .feature-item, .stat-card').forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });

    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
});

// Export utilities for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Utils, FileUploader, ApiClient, DownloadHandler };
}
