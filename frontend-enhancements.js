/*
 * Enhanced JavaScript for MoneyPrinter Frontend
 * Add this to Frontend/index.html before closing </body> tag
 */

// Progress tracking system
class VideoGenerationProgress {
    constructor() {
        this.steps = [
            { id: 'script', text: 'Generating Script...', progress: 20 },
            { id: 'search', text: 'Finding Videos...', progress: 40 },
            { id: 'audio', text: 'Creating Audio...', progress: 60 },
            { id: 'video', text: 'Assembling Video...', progress: 80 },
            { id: 'upload', text: 'Finalizing...', progress: 100 }
        ];
        this.currentStep = 0;
        this.setupProgressElements();
    }

    setupProgressElements() {
        // Add progress container if it doesn't exist
        if (!document.querySelector('.progress-container')) {
            const progressHTML = `
                <div class="progress-container" id="progressContainer">
                    <div class="progress-bar" id="progressBar"></div>
                    <div class="progress-steps" id="progressSteps">
                        ${this.steps.map(step => `
                            <span class="step" id="step-${step.id}">${step.text}</span>
                        `).join('')}
                    </div>
                </div>
                <div class="message" id="messageBox"></div>
            `;
            
            const form = document.querySelector('.max-w-xl');
            form.insertAdjacentHTML('afterbegin', progressHTML);
        }
    }

    show() {
        document.getElementById('progressContainer').style.display = 'block';
        this.updateProgress(0);
    }

    hide() {
        document.getElementById('progressContainer').style.display = 'none';
        this.currentStep = 0;
    }

    updateProgress(stepIndex) {
        if (stepIndex >= this.steps.length) return;
        
        this.currentStep = stepIndex;
        const step = this.steps[stepIndex];
        
        // Update progress bar
        document.getElementById('progressBar').style.width = step.progress + '%';
        
        // Update step indicators
        this.steps.forEach((s, index) => {
            const element = document.getElementById(`step-${s.id}`);
            element.classList.remove('active', 'completed');
            
            if (index < stepIndex) {
                element.classList.add('completed');
            } else if (index === stepIndex) {
                element.classList.add('active');
            }
        });
    }

    nextStep() {
        if (this.currentStep < this.steps.length - 1) {
            this.updateProgress(this.currentStep + 1);
        }
    }

    complete() {
        this.updateProgress(this.steps.length - 1);
        setTimeout(() => this.hide(), 2000);
    }

    error(message) {
        this.showMessage(message, 'error');
        this.hide();
    }

    showMessage(text, type = 'success') {
        const messageBox = document.getElementById('messageBox');
        messageBox.textContent = text;
        messageBox.className = `message ${type}`;
        messageBox.style.display = 'block';
        
        if (type === 'success') {
            setTimeout(() => {
                messageBox.style.display = 'none';
            }, 5000);
        }
    }
}

// Enhanced video generation with progress tracking
const progressTracker = new VideoGenerationProgress();

// Enhanced generate function
const generateVideoEnhanced = async () => {
    console.log("Generating video with progress tracking...");
    
    // Get form values
    const videoSubjectValue = document.querySelector("#videoSubject").value.trim();
    const voiceValue = document.querySelector("#voice").value;
    const youtubeUpload = document.querySelector("#youtubeUploadToggle").checked;
    
    // Validation
    if (!videoSubjectValue) {
        progressTracker.showMessage("Please enter a video subject", "error");
        return;
    }
    
    // UI updates
    const generateButton = document.querySelector("#generateButton");
    const cancelButton = document.querySelector("#cancelButton");
    
    generateButton.disabled = true;
    generateButton.classList.add("btn-generating");
    generateButton.textContent = "Generating...";
    cancelButton.classList.remove("hidden");
    
    // Show progress
    progressTracker.show();
    
    try {
        // Simulate progress updates (in real implementation, backend would send these)
        const simulateProgress = () => {
            const intervals = [2000, 3000, 4000, 3000]; // Time for each step
            
            intervals.forEach((delay, index) => {
                setTimeout(() => {
                    progressTracker.nextStep();
                }, intervals.slice(0, index + 1).reduce((a, b) => a + b, 0));
            });
        };
        
        simulateProgress();
        
        // Make API call
        const response = await fetch("http://localhost:8080/api/generate", {
            method: "POST",
            body: JSON.stringify({
                videoSubject: videoSubjectValue,
                voice: voiceValue,
                automateYoutubeUpload: youtubeUpload,
            }),
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
        });
        
        const data = await response.json();
        
        if (data.status === "success") {
            progressTracker.complete();
            progressTracker.showMessage(data.message, "success");
            
            // Optional: Show preview modal
            // showPreviewModal(data.data);
        } else {
            throw new Error(data.message);
        }
        
    } catch (error) {
        console.error("Generation error:", error);
        progressTracker.error("An error occurred. Please try again later.");
    } finally {
        // Reset UI
        generateButton.disabled = false;
        generateButton.classList.remove("btn-generating");
        generateButton.textContent = "Generate";
        cancelButton.classList.add("hidden");
    }
};

// Video format selector
function initializeFormatSelector() {
    const formatHTML = `
        <label class="text-blue-600">Video Format</label>
        <div class="format-selector">
            <div class="format-option selected" data-format="shorts">
                <span class="format-icon">📱</span>
                <div class="format-title">YouTube Shorts</div>
                <div class="format-desc">9:16 • Vertical</div>
            </div>
            <div class="format-option" data-format="square">
                <span class="format-icon">⬜</span>
                <div class="format-title">Instagram</div>
                <div class="format-desc">1:1 • Square</div>
            </div>
            <div class="format-option" data-format="landscape">
                <span class="format-icon">🖥️</span>
                <div class="format-title">YouTube</div>
                <div class="format-desc">16:9 • Landscape</div>
            </div>
        </div>
    `;
    
    // Insert after voice selector
    const voiceSection = document.querySelector("#voice").parentElement;
    voiceSection.insertAdjacentHTML('afterend', formatHTML);
    
    // Add click handlers
    document.querySelectorAll('.format-option').forEach(option => {
        option.addEventListener('click', () => {
            document.querySelectorAll('.format-option').forEach(o => o.classList.remove('selected'));
            option.classList.add('selected');
        });
    });
}

// Initialize enhancements when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Replace the original generate button event listener
    const generateButton = document.querySelector("#generateButton");
    generateButton.removeEventListener("click", generateVideo); // Remove original
    generateButton.addEventListener("click", generateVideoEnhanced); // Add enhanced
    
    // Initialize format selector
    initializeFormatSelector();
    
    console.log("MoneyPrinter enhancements loaded!");
});

// Utility functions
function getSelectedFormat() {
    return document.querySelector('.format-option.selected')?.dataset.format || 'shorts';
}

function showPreviewModal(videoPath) {
    const modalHTML = `
        <div class="modal" id="previewModal">
            <div class="modal-content">
                <h3 style="margin-bottom: 20px;">Video Preview</h3>
                <video controls src="../temp/${videoPath}"></video>
                <div class="modal-buttons">
                    <button class="btn-primary" onclick="confirmVideo()">Looks Great!</button>
                    <button class="btn-secondary" onclick="closePreview()">Close</button>
                </div>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closePreview() {
    const modal = document.getElementById('previewModal');
    if (modal) modal.remove();
}

function confirmVideo() {
    progressTracker.showMessage("Video confirmed! Check the temp folder for your file.", "success");
    closePreview();
}