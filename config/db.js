const mongoose = require('mongoose');

const connectDB = async () => {
    try {
        const uri = process.env.MONGODB_URI;
        
        if (!uri || uri.includes('<username>')) {
            console.warn('⚠️  MongoDB URI not configured. Running in fallback mode.');
            console.warn('   To connect MongoDB:');
            console.warn('   1. Create a free cluster at https://cloud.mongodb.com');
            console.warn('   2. Copy your connection string');
            console.warn('   3. Update MONGODB_URI in .env file');
            return false;
        }

        await mongoose.connect(uri);
        console.log('✅ MongoDB connected successfully');
        return true;
    } catch (error) {
        console.error('❌ MongoDB connection failed:', error.message);
        return false;
    }
};

module.exports = connectDB;
