const express = require("express");

const router = express.Router();

const sentimentController =
    require("../controllers/sentimentController");


router.post(
    "/predict",
    sentimentController.predictSentiment
);


module.exports = router;