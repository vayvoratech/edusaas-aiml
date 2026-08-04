const express = require("express");
const cors = require("cors");

const quizRoutes = require("./routes/quiz");

const app = express();

app.use(express.json());

app.use(cors());

app.use("/api/quiz", quizRoutes);

module.exports = app;