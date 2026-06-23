// Global State
let farmers = [];
var currentQualityData = {};

const API_URL = '/api';

// --- Firebase Authentication Guard ---
let firebaseAuth = null;

async function checkAuthentication() {
    try {
        const response = await fetch('/api/firebase-config');
        const config = await response.json();

        // If Firebase credentials are not set in .env, skip auth guard to allow access
        if (!config.apiKey) {
            console.warn("⚠️ Firebase credentials not configured in .env. Skipping login guard.");
            return;
        }

        // Initialize Firebase
        firebase.initializeApp(config);
        firebaseAuth = firebase.auth();

        // Listen for authentication changes
        firebaseAuth.onAuthStateChanged((user) => {
            if (!user) {
                // Redirect to login page if unauthorized
                window.location.href = 'login.html';
            } else {
                // Show user email in topbar
                const emailSpan = document.getElementById('user-email');
                if (emailSpan) {
                    emailSpan.textContent = user.email;
                }
            }
        });

        // Setup Logout event listener
        const logoutBtn = document.getElementById('btn-logout');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async () => {
                try {
                    await firebaseAuth.signOut();
                } catch (err) {
                    console.error("Sign out failed:", err);
                }
            });
        }

    } catch (err) {
        console.error("Error setting up Firebase Authentication:", err);
    }
}

checkAuthentication();

// --- UI Navigation ---
document.querySelectorAll('.nav-links li').forEach(item => {
    item.addEventListener('click', () => {
        // Update active nav
        document.querySelectorAll('.nav-links li').forEach(nav => nav.classList.remove('active'));
        item.classList.add('active');

        // Update active module
        const target = item.getAttribute('data-target');
        document.querySelectorAll('.module-section').forEach(section => {
            section.classList.remove('active');
        });
        document.getElementById(target).classList.add('active');

        // Update Title
        const titleText = item.textContent.trim();
        document.getElementById('page-title').textContent = titleText;
    });
});

// --- Toast Notification ---
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// --- 1. Farmer Details Module ---
const farmerForm = document.getElementById('farmer-form');
const farmerTableBody = document.querySelector('#farmer-table tbody');
const qFarmerSelect = document.getElementById('q-farmer');

async function fetchFarmers() {
    try {
        const response = await fetch(`${API_URL}/farmers`);
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        farmers = await response.json();
        renderFarmers();
        populateFarmerSelect();
    } catch (error) {
        console.error('Error fetching farmers:', error);
        showToast('Failed to load farmers from server', 'error');
    }
}

function renderFarmers() {
    farmerTableBody.innerHTML = '';
    if (farmers.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="6" style="text-align:center;color:#888;padding:20px;">No farmers registered yet. Add one above!</td>';
        farmerTableBody.appendChild(tr);
        return;
    }
    farmers.forEach(farmer => {
        // MongoDB returns _id mapped as 'id' in our server response
        const farmerId = farmer['f-id'] || farmer.farmerId || '';
        const farmerDbId = farmer.id || farmer._id || '';
        const farmerName = farmer['f-name'] || farmer.name || '';
        const farmerPhone = farmer['f-phone'] || farmer.phone || '';
        const farmerCows = farmer['f-cows'] !== undefined ? farmer['f-cows'] : (farmer.cows || 0);
        const farmerBuffaloes = farmer['f-buffaloes'] !== undefined ? farmer['f-buffaloes'] : (farmer.buffaloes || 0);
        const farmerSupply = farmer['f-supply'] !== undefined ? farmer['f-supply'] : (farmer.dailySupply || 0);
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${farmerId}</td>
            <td>${farmerName}</td>
            <td>${farmerPhone}</td>
            <td>${farmerCows} / ${farmerBuffaloes}</td>
            <td>${farmerSupply} L</td>
            <td class="action-btns">
                <button class="icon-btn delete" onclick="deleteFarmer('${farmerDbId}')"><i class="fa-solid fa-trash"></i></button>
            </td>
        `;
        farmerTableBody.appendChild(tr);
    });
}

function populateFarmerSelect() {
    qFarmerSelect.innerHTML = '<option value="">-- Select Farmer --</option>';
    farmers.forEach(farmer => {
        const id = farmer.id || farmer['f-id'];
        const name = farmer.name || farmer['f-name'];
        const option = document.createElement('option');
        option.value = id;
        option.textContent = `${id} - ${name}`;
        qFarmerSelect.appendChild(option);
    });
}

farmerForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Basic client-side validation
    const fId = document.getElementById('f-id').value.trim();
    const fName = document.getElementById('f-name').value.trim();
    const fPhone = document.getElementById('f-phone').value.trim();
    const fAddress = document.getElementById('f-address').value.trim();
    const fBank = document.getElementById('f-bank').value.trim();
    const fCenter = document.getElementById('f-center').value.trim();

    if (!fId || !fName || !fPhone || !fAddress || !fBank || !fCenter) {
        showToast('Please fill in all required fields', 'error');
        return;
    }

    const newFarmer = {
        'f-id': fId,
        'f-name': fName,
        'f-phone': fPhone,
        'f-address': fAddress,
        'f-cows': parseInt(document.getElementById('f-cows').value) || 0,
        'f-buffaloes': parseInt(document.getElementById('f-buffaloes').value) || 0,
        'f-bank': fBank,
        'f-center': fCenter,
        'f-supply': parseFloat(document.getElementById('f-supply').value) || 0
    };

    // Show loading state on button
    const submitBtn = farmerForm.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    submitBtn.textContent = 'Saving...';
    submitBtn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/farmers`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(newFarmer)
        });

        const data = await response.json();

        if (response.ok) {
            showToast(`Farmer "${fName}" added successfully! ✅`);
            farmerForm.reset();
            fetchFarmers();
        } else {
            // Show the actual server error message (e.g. "Farmer ID already exists")
            const errorMsg = data.error || 'Failed to add farmer. Please try again.';
            showToast(errorMsg, 'error');
        }
    } catch (error) {
        console.error('Save farmer error:', error);
        showToast('Network error — could not connect to server.', 'error');
    } finally {
        submitBtn.textContent = originalText;
        submitBtn.disabled = false;
    }
});

async function deleteFarmer(id) {
    if (!id) {
        showToast('Cannot delete: invalid farmer ID', 'error');
        return;
    }
    if (confirm('Are you sure you want to delete this farmer?')) {
        try {
            const response = await fetch(`${API_URL}/farmers/${id}`, { method: 'DELETE' });
            if (response.ok) {
                showToast('Farmer deleted successfully');
                fetchFarmers();
            } else {
                showToast('Failed to delete farmer', 'error');
            }
        } catch (error) {
            console.error('Delete farmer error:', error);
            showToast('Network error — could not delete farmer', 'error');
        }
    }
}

// Search functionality
['input', 'keyup'].forEach(evt => {
    document.getElementById('search-farmer').addEventListener(evt, function(e) {
        const term = e.target.value.toLowerCase();
        const rows = farmerTableBody.querySelectorAll('tr');
        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(term) ? '' : 'none';
        });
    });
});

// --- 2. Milk Quality Module ---
function calculateBaseQuality() {
    const qty = parseFloat(document.getElementById('q-quantity').value);
    const fat = parseFloat(document.getElementById('q-fat').value);
    const snf = parseFloat(document.getElementById('q-snf').value);
    const farmerId = document.getElementById('q-farmer').value;

    if (!farmerId || isNaN(qty) || isNaN(fat) || isNaN(snf)) {
        showToast('Please fill all required fields correctly', 'error');
        return;
    }

    // Save state
    currentQualityData = { farmerId, qty, fat, snf };

    // Simple initial quality score based on Fat & SNF
    // Ideal cow: Fat >= 3.5, SNF >= 8.5 (Score 100)
    // Ideal buffalo: Fat >= 6.0, SNF >= 9.0 (Score 100)
    let score = 100;
    
    if (fat < 3.5) score -= (3.5 - fat) * 10;
    if (snf < 8.5) score -= (8.5 - snf) * 10;
    
    score = Math.max(0, Math.min(100, Math.round(score)));
    currentQualityData.baseScore = score;

    document.getElementById('base-score').textContent = score;
    const statusEl = document.getElementById('q-status');
    
    if (score >= 90) { statusEl.textContent = 'Excellent'; statusEl.style.backgroundColor = '#d1fae5'; statusEl.style.color = '#065f46'; }
    else if (score >= 75) { statusEl.textContent = 'Good'; statusEl.style.backgroundColor = '#e0f2fe'; statusEl.style.color = '#0369a1'; }
    else { statusEl.textContent = 'Average / Poor'; statusEl.style.backgroundColor = '#fee2e2'; statusEl.style.color = '#991b1b'; }

    document.getElementById('quality-result-card').style.display = 'block';
}

function goToAdulteration() {
    document.querySelector('.nav-links li[data-target="adulteration"]').click();
}

// --- 3. Adulteration Detection Module ---
function analyzeAdulteration() {
    if (!currentQualityData.baseScore) {
        showToast('Please complete Milk Quality Analysis first', 'error');
        return;
    }

    const water = parseFloat(document.getElementById('a-water').value) || 0;
    const urea = document.getElementById('a-urea').value;
    const starch = document.getElementById('a-starch').value;
    const detergent = document.getElementById('a-detergent').value;
    const salt = document.getElementById('a-salt').value;

    let finalScore = currentQualityData.baseScore;
    let warnings = [];
    let isAdulterated = false;

    if (water > 5) {
        finalScore -= (water - 5) * 2; // -2 points for every % above 5%
        warnings.push(`Water dilution detected: ${water}%`);
    }

    if (starch === 'Yes') { finalScore -= 20; warnings.push('Starch contamination detected (Score -20)'); isAdulterated = true; }
    if (salt === 'Yes') { finalScore -= 15; warnings.push('Salt contamination detected (Score -15)'); isAdulterated = true; }
    if (urea === 'Yes') { finalScore -= 50; warnings.push('CRITICAL: Urea detected (Score -50)'); isAdulterated = true; }
    if (detergent === 'Yes') { finalScore -= 60; warnings.push('CRITICAL: Detergent detected (Score -60)'); isAdulterated = true; }

    finalScore = Math.max(0, Math.round(finalScore));
    currentQualityData.finalScore = finalScore;

    // Update UI
    document.getElementById('final-score').textContent = finalScore;
    
    const warningList = document.getElementById('warning-messages');
    warningList.innerHTML = '';
    warnings.forEach(w => {
        const li = document.createElement('li');
        li.textContent = w;
        warningList.appendChild(li);
    });

    const statusEl = document.getElementById('adulteration-status');
    statusEl.className = 'alert';
    
    if (warnings.length === 0 && water <= 5) {
        statusEl.textContent = 'Pure Milk';
        statusEl.classList.add('pure');
    } else if (isAdulterated || finalScore < 50) {
        statusEl.textContent = 'Highly Adulterated';
        statusEl.classList.add('high');
    } else {
        statusEl.textContent = 'Moderately Adulterated';
        statusEl.classList.add('moderate');
    }

    document.getElementById('adulteration-result-card').style.display = 'block';

    // Save quality analysis record to database
    const qualityRecord = {
        farmerId: currentQualityData.farmerId,
        quantity: currentQualityData.qty,
        fat: currentQualityData.fat,
        snf: currentQualityData.snf,
        milkType: document.getElementById('q-type').value,
        protein: parseFloat(document.getElementById('q-protein').value) || null,
        lactose: parseFloat(document.getElementById('q-lactose').value) || null,
        temperature: parseFloat(document.getElementById('q-temp').value) || null,
        baseScore: currentQualityData.baseScore,
        finalScore: finalScore,
        waterDilution: water,
        ureaDetected: urea === 'Yes',
        starchDetected: starch === 'Yes',
        detergentDetected: detergent === 'Yes',
        saltDetected: salt === 'Yes',
        isAdulterated: isAdulterated,
        warnings: warnings
    };
    fetch(`${API_URL}/quality`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(qualityRecord)
    }).then(() => console.log('Quality record saved to database'))
      .catch(err => console.warn('Failed to save quality record:', err));

    // Update Payment Summary
    document.getElementById('summary-qty').textContent = `${currentQualityData.qty} L`;
    document.getElementById('summary-fat').textContent = `${currentQualityData.fat} %`;
    document.getElementById('summary-snf').textContent = `${currentQualityData.snf} %`;
    document.getElementById('summary-score').textContent = `${finalScore} / 100`;
}

function goToPayment() {
    document.querySelector('.nav-links li[data-target="payment-system"]').click();
}

// --- 4. Payment System Module ---
async function calculateFinalPrice() {
    if (!currentQualityData.finalScore && currentQualityData.finalScore !== 0) {
        showToast('Please complete Quality & Adulteration analysis', 'error');
        return;
    }

    const state = document.getElementById('p-state').value;
    if (!state) {
        showToast('Please select a state', 'error');
        return;
    }

    document.getElementById('payment-details').style.display = 'none';
    document.getElementById('payment-loading').style.display = 'block';

    const payload = {
        state: state,
        fat: currentQualityData.fat,
        snf: currentQualityData.snf,
        quantity: currentQualityData.qty,
        quality_score: currentQualityData.finalScore
    };

    try {
        const response = await fetch(`${API_URL}/calculate-price`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (!response.ok || !data.success) {
            throw new Error(data.error || 'Failed to calculate price');
        }

        // Update UI
        document.getElementById('p-formula-used').textContent = getFormulaText(state);
        document.getElementById('p-base-price').textContent = `₹${data.base_price_per_litre.toFixed(2)}`;
        document.getElementById('p-final-price').textContent = `₹${data.final_price_per_litre.toFixed(2)}`;
        
        animateCounter('p-total', data.total_payment);

        document.getElementById('payment-loading').style.display = 'none';
        document.getElementById('payment-details').style.display = 'block';

    } catch (error) {
        console.error(error);
        document.getElementById('payment-loading').style.display = 'none';
        showToast(error.message, 'error');
    }
}

function getFormulaText(state) {
    const formulas = {
        "Tamil Nadu": "Price = (Fat × 7) + (SNF × 3)",
        "Kerala": "Price = (Fat × 6.8) + (SNF × 3.2)",
        "Gujarat": "Price = (Fat × 6.5) + (SNF × 4)",
        "Maharashtra": "Price = Fat × 8",
        "Karnataka": "Price = Base(30) + Fat Incentive(>3.5) + Subsidy(5)",
        "Punjab": "Price = (Fat × 7.5) + (SNF × 2.5)",
        "Haryana": "Price = (Fat × 7.2) + (SNF × 2.8)"
    };
    return formulas[state] || "Standard Formula";
}

function animateCounter(id, finalValue) {
    const el = document.getElementById(id);
    let current = 0;
    const increment = finalValue / 20; // 20 frames
    const interval = setInterval(() => {
        current += increment;
        if (current >= finalValue) {
            current = finalValue;
            clearInterval(interval);
        }
        el.textContent = `₹${current.toFixed(2)}`;
    }, 30);
}

function processPayment() {
    const farmerId = currentQualityData.farmerId || 'unknown';
    const totalPayment = parseFloat(document.getElementById('p-total').textContent.replace('₹', '')) || 0;
    const state = document.getElementById('p-state').value;
    const basePrice = parseFloat(document.getElementById('p-base-price').textContent.replace('₹', '')) || 0;
    const finalPrice = parseFloat(document.getElementById('p-final-price').textContent.replace('₹', '')) || 0;

    const paymentData = {
        farmerId,
        farmerName: farmers.find(f => (f.id || f['f-id']) === farmerId)?.['f-name'] || '',
        quantity: currentQualityData.qty,
        fat: currentQualityData.fat,
        snf: currentQualityData.snf,
        qualityScore: currentQualityData.finalScore,
        state: state,
        basePricePerLitre: basePrice,
        finalPricePerLitre: finalPrice,
        totalPayment: totalPayment
    };

    // Save to server API (MongoDB)
    fetch(`${API_URL}/payments`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(paymentData)
    }).then(res => res.json())
      .then(() => showToast('Payment processed & saved to database!'))
      .catch(() => showToast('Payment processed successfully!'));

    setTimeout(() => { location.reload(); }, 2500);
}

// Init
fetchFarmers();
