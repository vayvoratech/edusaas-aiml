const express = require("express");

const {
    predictFraud
} = require("../controllers/fraudController");

const router = express.Router();

router.post(
    "/predict",
    predictFraud
);

module.exports = router;