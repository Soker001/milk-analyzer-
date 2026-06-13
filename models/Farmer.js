const mongoose = require('mongoose');

const farmerSchema = new mongoose.Schema({
    farmerId:   { type: String, required: true, unique: true },  // e.g. F001
    name:       { type: String, required: true },
    phone:      { type: String, required: true },
    address:    { type: String },
    cows:       { type: Number, default: 0 },
    buffaloes:  { type: Number, default: 0 },
    bankAccount:{ type: String },
    center:     { type: String },
    dailySupply:{ type: Number, default: 0 }
}, { timestamps: true });

module.exports = mongoose.model('Farmer', farmerSchema);
