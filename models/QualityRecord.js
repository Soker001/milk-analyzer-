const mongoose = require('mongoose');

const qualityRecordSchema = new mongoose.Schema({
    farmerId:           { type: String, required: true },
    quantity:           { type: Number, required: true },
    fat:                { type: Number, required: true },
    snf:                { type: Number, required: true },
    milkType:           { type: String, enum: ['Cow', 'Buffalo', 'Mixed'], default: 'Cow' },
    protein:            { type: Number },
    lactose:            { type: Number },
    temperature:        { type: Number },
    baseScore:          { type: Number },
    finalScore:         { type: Number },
    waterDilution:      { type: Number, default: 0 },
    ureaDetected:       { type: Boolean, default: false },
    starchDetected:     { type: Boolean, default: false },
    detergentDetected:  { type: Boolean, default: false },
    saltDetected:       { type: Boolean, default: false },
    isAdulterated:      { type: Boolean, default: false },
    warnings:           [{ type: String }]
}, { timestamps: true });

module.exports = mongoose.model('QualityRecord', qualityRecordSchema);
