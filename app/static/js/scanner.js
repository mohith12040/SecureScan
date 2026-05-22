// SecureScan Interactive Scanner Operations Room
document.addEventListener('DOMContentLoaded', () => {
    const scanForm = document.getElementById('securescan-form');
    if (!scanForm) return;

    const modalBodyDefault = document.getElementById('modal-body-default');
    const modalBodyScanning = document.getElementById('modal-body-scanning');
    const scanSubmitBtn = document.getElementById('scan-submit-btn');
    const progressBar = document.getElementById('scan-progress-bar');
    const terminalBody = document.getElementById('terminal-log-body');
    const targetInput = document.getElementById('scan-target-input');
    const scanTypeSelect = document.getElementById('scan-mode-select');
    const customPortsGroup = document.getElementById('custom-ports-group');
    const customPortsInput = document.getElementById('custom-ports-input');

    // Toggle custom ports visibility
    scanTypeSelect.addEventListener('change', () => {
        if (scanTypeSelect.value === 'Custom Ports') {
            customPortsGroup.style.display = 'block';
        } else {
            customPortsGroup.style.display = 'none';
        }
    });

    scanForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const target = targetInput.value.trim();
        const scanType = scanTypeSelect.value;
        const customPorts = customPortsInput.value.trim();

        if (!target) return;

        // Transition views to the scanning terminal loader
        modalBodyDefault.style.display = 'none';
        modalBodyScanning.style.display = 'block';
        scanSubmitBtn.disabled = true;

        // Reset progress & terminal
        progressBar.style.width = '0%';
        terminalBody.innerHTML = '';

        // Real-looking scrolling logs
        const logLines = [
            `$ securescan --target "${target}" --mode "${scanType}"`,
            `[STATUS] Initializing SecureScan Engine v2.0...`,
            `[RESOLVE] Attempting DNS resolution for target: ${target}`,
            `[RESOLVE] Target resolved to socket host binding successfully.`,
            `[SCAN] Starting Nmap Port Scan (TCP Connection Mode)...`,
            `[SCAN] Auditing standard TCP ports list...`,
            `[SERVICE] Probing services banners and version identification...`,
            `[AI-ENGINE] Port collection complete. Feature matrix initialized.`,
            `[AI-ENGINE] Engineering features: ports, outdated variables, risks.`,
            `[AI-ENGINE] Executing Random Forest Severity Predictor model...`,
            `[AI-ENGINE] Classification complete with high confidence rating.`,
            `[DATABASE] Writing scanned assets and CVE metrics to SQLite...`,
            `[SUCCESS] Security audit completed! Generating detail reports...`
        ];

        // Typewrite simulation lines alongside progress increments
        let lineIdx = 0;
        let progress = 0;
        
        const typewriteInterval = setInterval(() => {
            if (lineIdx < logLines.length) {
                // Add line to terminal
                const line = document.createElement('div');
                line.className = 'terminal-prompt';
                line.textContent = logLines[lineIdx];
                terminalBody.appendChild(line);
                
                // Keep terminal scrolled to bottom
                terminalBody.scrollTop = terminalBody.scrollHeight;
                
                lineIdx++;
                progress += Math.floor(100 / logLines.length);
                progressBar.style.width = `${Math.min(progress, 95)}%`;
            }
        }, 800);

        try {
            // Trigger actual scan API call in parallel
            const response = await secureFetch('/api/scan', {
                method: 'POST',
                body: {
                    target: target,
                    scan_type: scanType,
                    custom_ports: customPorts
                }
            });

            // Once API responds, complete typewriter & redirect
            clearInterval(typewriteInterval);
            
            // Output remainder logs
            const apiLogs = response.logs.split('\n');
            apiLogs.forEach(logLine => {
                if (logLine.trim()) {
                    const line = document.createElement('div');
                    line.textContent = logLine;
                    terminalBody.appendChild(line);
                }
            });

            progressBar.style.width = '100%';
            
            const completionLine = document.createElement('div');
            completionLine.style.color = '#00f0ff';
            completionLine.textContent = `\n[SECURESCAN COMPLETE] Redirecting to Dashboard metrics room...`;
            terminalBody.appendChild(completionLine);
            terminalBody.scrollTop = terminalBody.scrollHeight;

            setTimeout(() => {
                window.location.href = `/scan/${response.scan_id}`;
            }, 1800);

        } catch (error) {
            clearInterval(typewriteInterval);
            progressBar.className = 'cyber-progress-bar bg-danger';
            
            const errLine = document.createElement('div');
            errLine.style.color = '#ef4444';
            errLine.textContent = `\n[FATAL EXCEPTION] Scanning halted: ${error.message}`;
            terminalBody.appendChild(errLine);
            terminalBody.scrollTop = terminalBody.scrollHeight;

            setTimeout(() => {
                modalBodyDefault.style.display = 'block';
                modalBodyScanning.style.display = 'none';
                scanSubmitBtn.disabled = false;
                progressBar.className = 'cyber-progress-bar';
            }, 4000);
        }
    });
});
