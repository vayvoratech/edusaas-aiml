const express = require("express");
const cors = require("cors");

const recommendationRoutes = require("./routes/recommendation");

const dropoutRouter = require("./routes/dropout");
const sentimentRouter = require("./routes/sentiment");
const fraudRoutes = require("./routes/fraudRoutes");
const toxicityRoutes = require("./routes/toxicityRoutes");
const hiringRoutes = require("./routes/hiringRoutes");

const app = express();

app.use(cors());
app.use(express.json());

app.use("/api/recommendation", recommendationRoutes);

app.use("/api/dropout", dropoutRouter);
app.use("/api/sentiment", sentimentRouter);
app.use("/api/fraud", fraudRoutes);
app.use("/api/toxicity", toxicityRoutes);
app.use("/api/hiring", hiringRoutes);

module.exports = app;