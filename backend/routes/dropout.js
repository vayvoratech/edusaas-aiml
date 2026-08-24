const express = require("express");

const router = express.Router();

const dropoutController =
    require(
        "../controllers/dropoutController"
    );


router.post(
    "/predict",
    dropoutController.predictDropout
);


module.exports = router;