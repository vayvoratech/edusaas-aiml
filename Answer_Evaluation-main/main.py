from flask import Flask, jsonify, request
from utils.xlnet_model import get_similarity_score

app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'service': 'Descriptive Answer Evaluation',
        'status': 'running'
    })


@app.route('/evaluate', methods=['POST'])
def evaluate():

    try:
        print("\n========================================")
        print("Request received at /evaluate")
        print("========================================")

        # ------------------------------------------------
        # Get JSON data from Node.js
        # ------------------------------------------------

        data = request.get_json()

        if not data:
            print("No JSON data received")

            return jsonify({
                'success': False,
                'error': 'Request body is required'
            }), 400


        # ------------------------------------------------
        # Get question, student answer and reference answer
        # ------------------------------------------------

        question_text = data.get('question_text', '').strip()

        student_answer_text = data.get(
            'student_answer_text',
            ''
        ).strip()

        reference_answer_text = data.get(
            'reference_answer_text',
            ''
        ).strip()


        print("Question:")
        print(question_text)

        print("\nStudent Answer:")
        print(student_answer_text)

        print("\nReference Answer:")
        print(reference_answer_text)


        # ------------------------------------------------
        # Validate data
        # ------------------------------------------------

        if not question_text:

            return jsonify({
                'success': False,
                'error': 'Question text is required'
            }), 400


        if not student_answer_text:

            return jsonify({
                'success': False,
                'error': 'Student answer is required'
            }), 400


        if not reference_answer_text:

            return jsonify({
                'success': False,
                'error': 'Reference answer is required'
            }), 400


        # ------------------------------------------------
        # Call YOUR EXISTING XLNet MODEL
        # ------------------------------------------------

        print("\nCalculating similarity score...")

        similarity_score = get_similarity_score(
            question_text,
            student_answer_text,
            reference_answer_text
        )


        print(
            f"XLNet similarity score: {similarity_score}"
        )


        # ------------------------------------------------
        # Keep your existing score adjustment
        # ------------------------------------------------

        if similarity_score >= 75:

            similarity_score += 20

        elif similarity_score >= 70 and similarity_score < 75:

            similarity_score += 18

        elif similarity_score < 65 and similarity_score >= 60:

            similarity_score += 16

        else:

            similarity_score -= 10


        print(
            f"Final similarity score: {similarity_score}"
        )


        # ------------------------------------------------
        # Return score to Node.js
        # ------------------------------------------------

        return jsonify({

            'success': True,

            'score': similarity_score

        }), 200


    except Exception as e:

        import traceback

        print("\n========================================")
        print("XLNet Evaluation Error")
        print("========================================")

        print(str(e))

        print(traceback.format_exc())


        return jsonify({

            'success': False,

            'error': str(e)

        }), 500


if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )