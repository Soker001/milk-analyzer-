require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { spawn } = require('child_process');
const connectDB = require('./config/db');

// Mongoose Models
const Farmer = require('./models/Farmer');
const QualityRecord = require('./models/QualityRecord');
const Payment = require('./models/Payment');

const app = express();
const port = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static('public'));

// Track MongoDB connection state
let isDBConnected = false;

// In-memory fallback
let fallbackFarmers = [];

// ---------------------------------------------------------
// FARMER ROUTES
// ---------------------------------------------------------

// Get all farmers
app.get('/api/farmers', async (req, res) => {
    if (isDBConnected) {
        try {
            const farmers = await Farmer.find().sort({ createdAt: -1 });
            // Map to match frontend expected format
            const mapped = farmers.map(f => ({
                id: f._id,
                'f-id': f.farmerId,
                'f-name': f.name,
                'f-phone': f.phone,
                'f-address': f.address,
                'f-cows': f.cows,
                'f-buffaloes': f.buffaloes,
                'f-bank': f.bankAccount,
                'f-center': f.center,
                'f-supply': f.dailySupply
            }));
            res.json(mapped);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    } else {
        res.json(fallbackFarmers);
    }
});

// Add new farmer
app.post('/api/farmers', async (req, res) => {
    const data = req.body;
    if (isDBConnected) {
        try {
            const farmer = new Farmer({
                farmerId:    data['f-id'],
                name:        data['f-name'],
                phone:       data['f-phone'],
                address:     data['f-address'],
                cows:        data['f-cows'] || 0,
                buffaloes:   data['f-buffaloes'] || 0,
                bankAccount: data['f-bank'],
                center:      data['f-center'],
                dailySupply: data['f-supply'] || 0
            });
            const saved = await farmer.save();
            res.status(201).json({ id: saved._id, ...data });
        } catch (error) {
            if (error.code === 11000) {
                res.status(400).json({ error: 'Farmer ID already exists' });
            } else {
                res.status(500).json({ error: error.message });
            }
        }
    } else {
        const newFarmer = { id: Date.now().toString(), ...data };
        fallbackFarmers.push(newFarmer);
        res.status(201).json(newFarmer);
    }
});

// Delete farmer
app.delete('/api/farmers/:id', async (req, res) => {
    const { id } = req.params;
    if (isDBConnected) {
        try {
            await Farmer.findByIdAndDelete(id);
            res.status(200).json({ message: 'Farmer deleted successfully' });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    } else {
        fallbackFarmers = fallbackFarmers.filter(f => f.id !== id);
        res.status(200).json({ message: 'Farmer deleted successfully' });
    }
});

// ---------------------------------------------------------
// QUALITY ANALYSIS ROUTES
// ---------------------------------------------------------

// Save quality analysis record
app.post('/api/quality', async (req, res) => {
    if (isDBConnected) {
        try {
            const record = new QualityRecord(req.body);
            const saved = await record.save();
            res.status(201).json({ id: saved._id, ...req.body });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    } else {
        res.status(201).json({ id: Date.now().toString(), ...req.body });
    }
});

// Get all quality records
app.get('/api/quality', async (req, res) => {
    if (isDBConnected) {
        try {
            const records = await QualityRecord.find().sort({ createdAt: -1 }).limit(50);
            res.json(records);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    } else {
        res.json([]);
    }
});

// ---------------------------------------------------------
// PAYMENT ROUTES
// ---------------------------------------------------------

// Save payment transaction
app.post('/api/payments', async (req, res) => {
    if (isDBConnected) {
        try {
            const payment = new Payment(req.body);
            const saved = await payment.save();
            res.status(201).json({ id: saved._id, ...req.body });
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    } else {
        res.status(201).json({ id: Date.now().toString(), ...req.body });
    }
});

// Get all payment records
app.get('/api/payments', async (req, res) => {
    if (isDBConnected) {
        try {
            const payments = await Payment.find().sort({ createdAt: -1 }).limit(50);
            res.json(payments);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    } else {
        res.json([]);
    }
});

// Get payments for a specific farmer
app.get('/api/payments/farmer/:farmerId', async (req, res) => {
    const { farmerId } = req.params;
    if (isDBConnected) {
        try {
            const payments = await Payment.find({ farmerId }).sort({ createdAt: -1 });
            res.json(payments);
        } catch (error) {
            res.status(500).json({ error: error.message });
        }
    } else {
        res.json([]);
    }
});

// ---------------------------------------------------------
// PRICING ROUTE
// ---------------------------------------------------------

app.post('/api/calculate-price', (req, res) => {
    const inputData = req.body;
    
    const pythonProcess = spawn('python', ['pricing_engine.py']);
    
    let dataString = '';
    let errorString = '';

    pythonProcess.stdin.write(JSON.stringify(inputData));
    pythonProcess.stdin.end();

    pythonProcess.stdout.on('data', (data) => {
        dataString += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
        errorString += data.toString();
        console.error(`Python Error: ${data}`);
    });

    pythonProcess.on('close', (code) => {
        if (code !== 0) {
            return res.status(500).json({ error: 'Failed to calculate price', details: errorString });
        }
        try {
            const result = JSON.parse(dataString);
            if (result.success) {
                res.json(result);
            } else {
                res.status(400).json({ error: result.error });
            }
        } catch (err) {
            res.status(500).json({ error: 'Invalid response from pricing engine', raw: dataString });
        }
    });
});

// ---------------------------------------------------------
// DATABASE STATUS
// ---------------------------------------------------------
app.get('/api/status', (req, res) => {
    res.json({
        database: isDBConnected ? 'MongoDB connected' : 'Fallback mode (in-memory)',
        collections: ['farmers', 'qualityrecords', 'payments'],
        server: 'running'
    });
});

// ---------------------------------------------------------
// START SERVER
// ---------------------------------------------------------
const startServer = async () => {
    isDBConnected = await connectDB();

    app.listen(port, () => {
        console.log(`Server is running on http://localhost:${port}`);
        if (!isDBConnected) {
            console.warn('⚠️  RUNNING IN FALLBACK MODE: Using in-memory storage.');
        } else {
            console.log('📦 MongoDB collections: farmers, qualityrecords, payments');
        }
    });
};

startServer();
