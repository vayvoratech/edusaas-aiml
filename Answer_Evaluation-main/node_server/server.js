require("dotenv").config();

const express = require("express");

const app = express();

app.use(express.json());

const descriptiveAnswerRoutes =
    require("./routes/descriptiveAnswerRoutes");

app.use(
    "/api/descriptive",
    descriptiveAnswerRoutes
);

const PORT = process.env.PORT || 3000;

app.listen(PORT, () => {
    console.log(`Node.js server running on port ${PORT}`);
});