const express = require("express");

const {
    predictToxicityController
} = require("../controllers/toxicityController");

const router = express.Router();

router.post(
    "/predict",
    predictToxicityController
);

module.exports = router;