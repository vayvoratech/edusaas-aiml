const express = require("express");

const {
    predictHiringController
} = require("../controllers/hiringController");


const router = express.Router();


router.post(
    "/predict",
    predictHiringController
);


module.exports = router;