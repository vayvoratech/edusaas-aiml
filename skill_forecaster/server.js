const express = require('express');
const skillDemandRouter = require('./routes/skillDemand');

const app = express();
app.use(express.json());

// Mount skill demand routes
app.use('/api/skill-demand', skillDemandRouter);

const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`Node.js Gateway running on http://localhost:${PORT}`);
});