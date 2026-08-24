async function getToxicityData(postId, postText) {

    if (!postId) {
        throw new Error("post_id is required.");
    }

    if (!postText) {
        throw new Error("post_text is required.");
    }

    return {
        post_id: postId,
        post_text: postText
    };
}


module.exports = {
    getToxicityData
};