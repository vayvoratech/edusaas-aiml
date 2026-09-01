const express = require("express");

const {
    submitFinalCode
} = require("../controllers/finalSubmissionController");

const router = express.Router();


router.post(
    "/final",
    submitFinalCode
);


module.exports = router;