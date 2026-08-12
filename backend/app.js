const express = require("express");
const cors = require("cors");

const quizRoutes = require("./routes/quiz");
const skillGapRoutes = require("./routes/skillGap");

const app = express();

app.use(cors());
app.use(express.json());

// Quiz APIs
app.use("/api/quiz", quizRoutes);

// Skill Gap APIs
app.use("/api/skill-gap", skillGapRoutes);

module.exports = app;