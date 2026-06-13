const mongoose = require('mongoose');

const paymentSchema = new mongoose.Schema({
    farmerId:           { type: String, required: true },
    farmerName:         { type: String },
    quantity:           { type: Number, required: true },
    fat:                { type: Number },
    snf:                { type: Number },
    qualityScore:       { type: Number },
    state:              { type: String },
    basePricePerLitre:  { type: Number },
    finalPricePerLitre: { type: Number },
    totalPayment:       { type: Number, required: true },
    status:             { type: String, default: 'completed' }
}, { timestamps: true });

module.exports = mongoose.model('Payment', paymentSchema);
